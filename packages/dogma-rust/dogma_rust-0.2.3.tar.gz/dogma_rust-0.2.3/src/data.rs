use crate::parallel::parallel_concatenate_buffers;
use std::borrow::{Borrow, Cow};
use numpy::{PyArrayDescrMethods, PyUntypedArray, PyUntypedArrayMethods};
use rayon::prelude::*;
use pyo3::prelude::*;

pub struct AwkwardArray<'a, T>
where T: Clone {
    pub content: Cow<'a, [T]>,
    pub cu_seqlens: Cow<'a, [isize]>,
}


impl<'a, T: Sync + Clone> AwkwardArray<'a, T> {
    pub fn new(content: impl Into<Cow<'a, [T]>>, cu_seqlens: impl Into<Cow<'a, [isize]>>) -> Self {
        AwkwardArray {
            content: content.into(),
            cu_seqlens: cu_seqlens.into(),
        }
    }

    pub fn parallel_concatenate(arrs: &[&AwkwardArray<'_, T>]) -> AwkwardArray<'static, T> {
        let content_buffers = arrs.iter().copied().map(|arr| arr.content.borrow()).collect::<Vec<_>>();
        let (cat_content, _) = parallel_concatenate_buffers(&content_buffers);

        let cu_seqlen_offsets = arrs.iter().copied().scan(0, |acc, arr| {
            let start = *acc;
            *acc += arr.cu_seqlens.last().copied().unwrap_or(0);
            Some(start)
        }).collect::<Vec<_>>();

        let shifted_cu_seqlens = arrs.par_iter().zip(cu_seqlen_offsets).map(|(arr, offset)| {
            let mut shifted = arr.cu_seqlens.clone().into_owned();
            shifted.iter_mut().for_each(|cu_seqlen| *cu_seqlen += offset);
            shifted
        }).collect::<Vec<_>>();
        let shifted_cu_seqlens_bufs = shifted_cu_seqlens.iter().map(|cu_seqlens| cu_seqlens.borrow()).collect::<Vec<_>>();

        let (out_cu_seqlens, _) = parallel_concatenate_buffers(&shifted_cu_seqlens_bufs);


        AwkwardArray::new(cat_content, out_cu_seqlens)
    }
}


pub trait TreatAsByteSlice<'a, T> {
    fn as_slice(&self) -> &'a [T];
}

impl<'a, T> TreatAsByteSlice<'a, T> for Bound<'a, PyUntypedArray> {
    fn as_slice(&self) -> &'a [T] {
        unsafe {
            assert!(self.is_contiguous());
            let arr = *self.as_array_ptr();
            let dtype_width = self.dtype().itemsize();
            std::slice::from_raw_parts(arr.data as *const T, self.len() * dtype_width as usize / std::mem::size_of::<T>())
        }
    }
}