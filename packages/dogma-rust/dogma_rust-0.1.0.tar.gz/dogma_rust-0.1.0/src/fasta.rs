use std::fs::read;
use rayon::prelude::*;
use crate::data::AwkwardArray;


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

fn parse_fasta_chunk(text: &[u8], start_i: usize, end_i: usize, mapping: &CharMapping) -> AwkwardArray<'static, u8> {
    let mut out_content = vec![];
    let mut out_cu_seqlens = vec![0];
    let mut i = start_i;

    let text_length = text.len();
    while i < text_length && unsafe { *text.get_unchecked(i) } != b'>' {
        // Move to first header
        i += 1;
    }

    let parse_char = |c: u8| {
        match c {
            b'A' => mapping.a,
            b'T' => mapping.t,
            b'C' => mapping.c,
            b'G' => mapping.g,
            _ => mapping.all_other,
        }
    };

    while i < text.len() {
        let c = unsafe { *text.get_unchecked(i) };
        
        if c == b'>' { // New header
            if i >= end_i { // Continue until a header shows up that has been handled by a later chunk.
                break;
            }
            // Maybe parse the header in the future?
            while i < text.len() && unsafe { *text.get_unchecked(i) } != b'\n' {
                i += 1;
            }
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
        }
    }

    AwkwardArray::new(out_content, out_cu_seqlens)
    
}


pub(crate) fn parse_fasta(path: &str, mapping: &[u8]) -> AwkwardArray<'static, u8>{
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

    let chunk_results: Vec<AwkwardArray<u8>> = (0..n_threads).par_bridge().map(|i| {
        let start_i = i * chunk_size;
        let end_i = std::cmp::min((i + 1) * chunk_size, total_length);
        let chunk_result = parse_fasta_chunk(&data, start_i, end_i, &char_mapping);
        chunk_result
    }).collect();


    println!("Merging result");
    let merged_result = AwkwardArray::parallel_concatenate(&chunk_results);
    drop(chunk_results);

    merged_result
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_big_fasta() {
        let fasta_path = "/lfs/local/0/roed/projects/dogma-data/fasta_data/result_rep_seq.fasta";
        let result = parse_fasta(fasta_path, &[1, 2, 3, 4, 5]);

        println!("Parsed fasta with {} sequences and {} tokens", result.cu_seqlens.len() - 1, result.content.len());
        std::hint::black_box(&result);
    }
}