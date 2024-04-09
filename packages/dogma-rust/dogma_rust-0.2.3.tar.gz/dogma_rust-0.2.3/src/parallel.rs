use rayon::prelude::*;

struct SendPtr<T>(*mut T);

// unsafe impl<T> Send for SendPtr<T> {}
unsafe impl<T> Sync for SendPtr<T> {}

pub fn parallel_concatenate_buffers<T: Sync>(bufs: &[&[T]]) -> (Vec<T>, Vec<usize>) {
    let out_buf_size = bufs.iter().map(|&buf| buf.len()).sum();

    let mut out_buf = Vec::with_capacity(out_buf_size);
    unsafe {out_buf.set_len(out_buf_size);}
    let data = SendPtr(out_buf.as_mut_ptr());

    let starting_indices = bufs.iter().scan(0, |acc, buf| {
        let start = *acc;
        *acc += buf.len();
        Some(start)
    }).collect::<Vec<_>>();

    starting_indices.par_iter().zip(bufs).for_each(|(&start, &buf)| {
        let buf_len = buf.len();
        let buf_ptr = buf.as_ptr();
        unsafe {
            let send_dest = &data;
            let dest_base: *mut T = send_dest.0;
            let dest: *mut T = dest_base.add(start);
            let src = buf_ptr;
            std::ptr::copy_nonoverlapping(src, dest, buf_len);
        }
    });
    
    (out_buf, starting_indices)
}



#[cfg(test)]
mod tests {
    use std::hint::black_box;

    use super::*;
    use rand::prelude::*;

    #[test]
    fn test_parallel_concatenate_buffers() {
        let bufs = (0..10_000).into_par_iter().map(|_| (0..1_000).map(|_| random::<u8>()).collect::<Vec<_>>()).collect::<Vec<_>>();
        let ref_bufs = bufs.iter().map(|buf| buf.as_slice()).collect::<Vec<_>>();
        eprintln!("Starting test");
        let (out_buf, _) = parallel_concatenate_buffers(&ref_bufs);
        eprintln!("Finished test");
        let flattened = bufs.iter().flatten().copied().collect::<Vec<_>>();
        assert_eq!(out_buf, flattened);
    }

    #[test]
    fn test_run_parallel_flatten() {
        let bufs = (0..100).into_par_iter().map(|_| (0..10_000_000).map(|_| random::<u8>()).collect::<Vec<_>>()).collect::<Vec<_>>();

        let ref_bufs = bufs.iter().map(|buf| buf.as_slice()).collect::<Vec<_>>();

        eprintln!("starting seq");
        // let seq_flat_buf: Vec<u8> = ref_bufs.iter().map(|&inner| inner.iter()).flatten().copied().collect();
        eprintln!("starting par");
        let par_flat_buf: Vec<u8> = ref_bufs.par_iter().map(|&inner| inner).flatten().copied().collect();
        eprintln!("starting par efficient");
        let (par_efficient_buf, _) = parallel_concatenate_buffers(&ref_bufs);
        eprintln!("finished");

        // Feed these to black box to stop them from being optimized away
        black_box(&par_flat_buf);
        black_box(&par_efficient_buf);


        assert_eq!(par_efficient_buf, par_flat_buf);
        // Conclusion: Clearly the parallel implementation writes in parallel, but it seems not super efficiently.
    }
}