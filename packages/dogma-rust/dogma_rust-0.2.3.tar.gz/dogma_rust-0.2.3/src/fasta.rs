use std::fs::read;
use rayon::prelude::*;
use crate::data::AwkwardArray;
use crate::parallel::parallel_concatenate_buffers;


struct CharMapping {
    a: u8,
    t: u8,
    c: u8,
    g: u8,
    all_other: u8,
}

impl CharMapping {
    pub fn from_mapping_vector(vec: &[u8]) -> Self {
        assert!(vec.len() == 5);
        CharMapping {
            a: vec[0],
            t: vec[1],
            c: vec[2],
            g: vec[3],
            all_other: vec[4],
        }
    }
}

pub struct ParsedFasta {
    pub sequences: AwkwardArray<'static, u8>,
    pub taxon_ids: Vec<u64>,
}

fn parse_fasta_chunk(text: &[u8], start_i: usize, end_i: usize, mapping: &CharMapping) -> ParsedFasta {
    let mut out_content = vec![];
    let mut out_cu_seqlens = vec![0];
    let mut out_taxon_ids = vec![];
    let mut i = start_i;

    let text_length = text.len();
    while i < text_length && unsafe { *text.get_unchecked(i) } != b'>' {
        // Move to first header
        i += 1;
    }

    let parse_char = |c: u8| {
        match c {
            b'A' => mapping.a,
            b'T' | b'U' => mapping.t,
            b'C' => mapping.c,
            b'G' => mapping.g,
            _ => mapping.all_other,
        }
    };

    let mut current_taxon_id: Option<u64> = None;

    while i < text.len() {
        let c = unsafe { *text.get_unchecked(i) };

        if c == b'>' { // New header
            if i >= end_i { // Continue until a header shows up that has been handled by a later chunk.
                break;
            }
            let taxon_id_start = i + 1;
            // Maybe parse the header in the future?
            while i < text.len() && unsafe { *text.get_unchecked(i) } != b'\n' {
                i += 1;
            }
            let taxon_id_end = i;
            let taxon_str = std::str::from_utf8(&text[taxon_id_start..taxon_id_end]).unwrap();
            current_taxon_id = Some(taxon_str.parse::<u64>().unwrap());
            i += 1; // Move to next line
            continue;
        } else { // Parse one line
            while i < text_length && unsafe { *text.get_unchecked(i) } != b'\n' {
                i += 1;
                unsafe {
                    out_content.push(parse_char(*text.get_unchecked(i)));
                }
            } // Ends if newline or end of file
            i += 1;
            out_cu_seqlens.push(out_content.len() as isize);
            out_taxon_ids.push(current_taxon_id.unwrap());
        }
    }

    ParsedFasta {
        sequences: AwkwardArray::new(out_content, out_cu_seqlens),
        taxon_ids: out_taxon_ids,
    }
    
}


pub(crate) fn parse_fasta(path: &str, mapping: &[u8]) -> ParsedFasta{
    assert!(mapping.len() == 5);

    // Read file
    println!("Reading file");
    let data = read(path).unwrap();

    let mut n_threads = rayon::current_num_threads();

    let total_length = data.len();

    if total_length < 100_000 {
        n_threads = 1;
    }

    let chunk_size = total_length.div_ceil(n_threads);

    let char_mapping = CharMapping::from_mapping_vector(mapping);

    println!("Parsing file {path} in chunks");

    let chunk_results: Vec<ParsedFasta> = (0..n_threads).par_bridge().map(|i| {
        let start_i = i * chunk_size;
        let end_i = std::cmp::min((i + 1) * chunk_size, total_length);
        let chunk_result = parse_fasta_chunk(&data, start_i, end_i, &char_mapping);
        chunk_result
    }).collect();


    println!("Merging result");
    let sequences_refs = chunk_results.iter().map(|pf| &pf.sequences).collect::<Vec<_>>();
    let taxon_ids = chunk_results.iter().map(|pf| pf.taxon_ids.as_slice()).collect::<Vec<_>>();

    let (merged_taxon_ids, _cu) = parallel_concatenate_buffers(&taxon_ids);
    let merged_sequences = AwkwardArray::parallel_concatenate(&sequences_refs);
    drop(chunk_results);

    ParsedFasta {
        sequences: merged_sequences,
        taxon_ids: merged_taxon_ids,
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_big_fasta() {
        let fasta_path = "/lfs/local/0/roed/projects/dogma-data/fasta_data/result_rep_seq.fasta";
        let result = parse_fasta(fasta_path, &[1, 2, 3, 4, 5]);

        println!("Parsed fasta with {} sequences and {} tokens", result.sequences.cu_seqlens.len() - 1, result.sequences.content.len());
        println!("Got the following taxon ids: {:?}", result.taxon_ids);
        std::hint::black_box(&result);
    }
}