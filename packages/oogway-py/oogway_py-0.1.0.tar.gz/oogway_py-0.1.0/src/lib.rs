use std::{pin::Pin, sync::Arc};

use async_openai::{error::OpenAIError, types::CreateChatCompletionStreamResponse};
use async_std::stream::IntoStream;
use ::oogway::{ask_helper, Oogway as _Oogway};
use futures::{Stream,StreamExt};
use pyo3::{
    exceptions::{PyKeyError, PyStopAsyncIteration},
    pyclass, pymethods, pymodule,
    types::PyModule,
    PyObject, PyRef, PyResult, Python,
};
use tokio::sync::Mutex;

#[pymodule]
fn oogway_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Oogway>()?;
    Ok(())
}


#[pyclass]
#[derive(Clone)]
pub struct Oogway {
    inner: _Oogway,
}

#[pymethods]
impl Oogway {
    #[new]
    fn new() -> PyResult<Oogway> {
        match _Oogway::new() {
            Ok(oogway) => Ok(Self { inner: oogway }),
            Err(e) => Err(PyKeyError::new_err(e.to_string())),
        }
    }

    #[setter(model_name)]
    fn set_model_name(&mut self, model_name: String) {
        self.inner.model(model_name);
    }

    // &PyAny
    pub fn ask(&mut self, _py: Python, question: String) -> PyResult<RespStream> {
        let i = self.inner.clone();
        let stream = pyo3_asyncio::tokio::get_runtime()
            .block_on(async { ask_helper(i, question).await.unwrap().into_stream() });
        Ok(RespStream {
            s: Arc::new(Mutex::new(stream)),
        })
    }
}


type S =  Arc<Mutex<Pin<Box<dyn Stream<Item = Result<CreateChatCompletionStreamResponse, OpenAIError>>+ Send>>>>;

#[pyo3::pyclass]
pub struct RespStream {
    s: S,
}

#[pymethods]
impl RespStream {
    fn __aiter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __anext__(&self, py: Python) -> PyResult<Option<PyObject>> {
        let f = self.s.clone();
        let future = pyo3_asyncio::tokio::future_into_py(py, async move {
            let val = f.lock().await.next().await;
            match val {
                Some(val) => Ok(val
                    .unwrap()
                    .choices
                    .iter()
                    .filter_map(|chat_choice| chat_choice.delta.content.clone())
                    .collect::<String>()),
                None => Err(PyStopAsyncIteration::new_err("The iterator is exhausted")),
            }
        });

        Ok(Some(future?.into()))
    }
}
