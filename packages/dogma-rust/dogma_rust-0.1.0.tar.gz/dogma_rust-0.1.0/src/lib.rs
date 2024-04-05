mod fasta;
mod data;
pub mod parallel;

use pyo3::prelude::*;
use pyo3::types::{PyList, PyTuple};
use numpy::{IntoPyArray, PyArray, PyArray1, PyArrayDescr, PyArrayDescrMethods, PyReadonlyArray1, PyUntypedArray, PyUntypedArrayMethods};
use crate::data::{AwkwardArray, TreatAsByteSlice};
use std::borrow::Borrow;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

impl<'a, T: Clone + Sync> From<Bound<'a, PyTuple>> for AwkwardArray<'a, T> {
    fn from(value: Bound<'a, PyTuple>) -> Self {
        let content = value.get_item(0);
        todo!()
        // AwkwardArray {

        // }
    }
}

#[pyfunction]
fn parse_fasta<'py>(py: Python<'py>, path: &str, mapping: PyReadonlyArray1<'py, u8>) -> PyResult<(Bound<'py, PyArray1<u8>>, Bound<'py, PyArray1<isize>>)> {
    let mapping = mapping.as_slice()?;

    let AwkwardArray {content, cu_seqlens} = fasta::parse_fasta(path, mapping);

    let content = content.into_owned().into_pyarray_bound(py);
    let cu_seqlens = cu_seqlens.into_owned().into_pyarray_bound(py);
    Ok((content, cu_seqlens))
}

#[pyfunction]
fn concatenate_awkward<'py>(py: Python<'py>, arrays: Bound<'py, PyList>) -> PyResult<(Bound<'py, PyArray1<u8>>, Bound<'py, PyArray1<isize>>)> {
    let awkwards: Vec<AwkwardArray<_>> = arrays.iter().map(|obj| {
        let tuple = obj.downcast::<PyTuple>()?;
        let tup_content = tuple.get_item(0)?;
        let tup_cu_seqlens = tuple.get_item(1)?;
        let content = tup_content.downcast::<PyUntypedArray>()?;
        let cu_seqlens = tup_cu_seqlens.downcast::<PyUntypedArray>()?;

        let content: &[u8] = content.as_slice();
        let cu_seqlens: &[isize] = cu_seqlens.as_slice();
        Ok(AwkwardArray::<u8>::new(content, cu_seqlens))
    }).collect::<PyResult<_>>()?;

    let AwkwardArray {content, cu_seqlens} = AwkwardArray::parallel_concatenate(&awkwards);

    Ok((content.into_owned().into_pyarray_bound(py), cu_seqlens.into_owned().into_pyarray_bound(py)))
}


#[pyfunction]
fn concatenate_numpy<'py>(py: Python<'py>, arrays: Bound<'py, PyList>) -> PyResult<Bound<'py, PyArray1<u8>>> {
    // Takes in a list of numpy arrays of the same dtype, and concatenates them into a single numpy array
    // The output array is always of dtype u8, so must be casted to the correct dtype after concatenation using `numpy.ndarray.view(dtype)`
    
    let buf_refs: Vec<_> = arrays.iter().map(|obj| -> PyResult<_> {
        let arr = obj.downcast::<PyUntypedArray>()?;
        Ok((arr.dtype(), unsafe{let arr = *arr.as_array_ptr(); arr.data}, arr.len(), arr.is_contiguous()))
    }).collect::<PyResult<_>>()?;
    let first_dtype = &buf_refs[0].0;

    let all_dtypes_match = buf_refs.iter().all(|(dtype, _ptr, _len, contiguous)| first_dtype.is_equiv_to(dtype) && *contiguous);
    if !all_dtypes_match {
        return Err(pyo3::exceptions::PyValueError::new_err("All arrays must have the same dtype and be contiguous"));
    }

    let itemsize = first_dtype.itemsize();

    let slices: Vec<&[u8]> = buf_refs.iter().map(|(_dtype, ptr, len, _contiguous)| unsafe { std::slice::from_raw_parts(*ptr as *const u8, len * itemsize) }).collect();

    let result: Vec<u8> = parallel::parallel_concatenate_buffers(&slices);
    
    let result_arr = result.into_pyarray_bound(py);

    Ok(result_arr)
}

/// A Python module implemented in Rust.
#[pymodule]
fn dogma_rust(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(parse_fasta, m)?)?;
    m.add_function(wrap_pyfunction!(concatenate_numpy, m)?)?;
    m.add_function(wrap_pyfunction!(concatenate_awkward, m)?)?;
    // m.add_function
    Ok(())
}
