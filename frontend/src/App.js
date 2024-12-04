import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import { Container, Form, Button, Alert, Spinner } from 'react-bootstrap';

function App() {
  const [url, setUrl] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const handleDownload = async (e) => {
    e.preventDefault(); // Prevent form reload
    setStatus('');
    setLoading(true); // Show loading spinner on button

    try {
      const response = await axios.post('http://localhost:5000/download', { url }); // Adjust backend URL for local dev
      setStatus(`Download complete: ${response.data.title}`);
    } catch (error) {
      console.error(error);
      if (error.response) {
        setStatus(`Error: ${error.response.data.error}`);
      } else if (error.request) {
        setStatus('Error: Network issue. Unable to connect to the server.');
      } else {
        setStatus(`Error: ${error.message}`);
      }
    } finally {
      setLoading(false); // Hide loading spinner after response
    }
  };

  return (
    <Container className="App">
      <h1 className="my-4 text-center">YouTube Video Downloader</h1>
      <Form onSubmit={handleDownload}>
        <Form.Group controlId="formBasicURL">
          <Form.Control
            type="text"
            placeholder="Enter YouTube video URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="mb-3"
          />
        </Form.Group>
        <Button
          variant="primary"
          type="submit"
          className="w-100"
          disabled={loading} // Disable button while loading
        >
          {loading ? (
            <>
              <Spinner animation="border" size="sm" className="me-2" />
              Downloading...
            </>
          ) : (
            'Download'
          )}
        </Button>
      </Form>

      {status && (
        <Alert
          variant={status.startsWith('Error') ? 'danger' : 'success'}
          className="mt-4"
        >
          {status}
        </Alert>
      )}
    </Container>
  );
}

export default App;
