import React, { useState } from 'react';
import { Form, Button, Alert, Card } from 'react-bootstrap';
import axios from 'axios';

const CandidateRegistration = () => {
  // Form state
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    date_of_birth: '',
    years_of_experience: '',
    department: '',
    resume: null
  });
  
  // Form submission state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [candidateId, setCandidateId] = useState(null);
  
  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  // Handle file input change
  const handleFileChange = (e) => {
    setFormData({
      ...formData,
      resume: e.target.files[0]
    });
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitError(null);
    
    // Create form data for file upload
    const submitData = new FormData();
    Object.keys(formData).forEach(key => {
      submitData.append(key, formData[key]);
    });
    
    try {
      const response = await axios.post('/api/candidates/register/', submitData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setSubmitSuccess(true);
      setCandidateId(response.data.id);
      
      // Reset form
      setFormData({
        full_name: '',
        email: '',
        date_of_birth: '',
        years_of_experience: '',
        department: '',
        resume: null
      });
      
      // Reset file input
      document.getElementById('resume').value = '';
      
    } catch (error) {
      console.error('Registration error:', error);
      setSubmitError(
        error.response?.data?.detail || 
        'An error occurred during registration. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <Card className="mb-4">
      <Card.Header as="h5">Candidate Registration</Card.Header>
      <Card.Body>
        {submitSuccess ? (
          <Alert variant="success">
            <Alert.Heading>Registration Successful!</Alert.Heading>
            <p>
              Your application has been submitted successfully. You can check your application status
              using your candidate ID: <strong>{candidateId}</strong>
            </p>
            <hr />
            <div className="d-flex justify-content-end">
              <Button 
                variant="outline-success"
                onClick={() => setSubmitSuccess(false)}
              >
                Register Another Candidate
              </Button>
            </div>
          </Alert>
        ) : (
          <Form onSubmit={handleSubmit}>
            {submitError && (
              <Alert variant="danger">
                {submitError}
              </Alert>
            )}
            
            <Form.Group className="mb-3" controlId="fullName">
              <Form.Label>Full Name</Form.Label>
              <Form.Control
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
                placeholder="Enter your full name"
              />
            </Form.Group>
            
            <Form.Group className="mb-3" controlId="email">
              <Form.Label>Email Address</Form.Label>
              <Form.Control
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="Enter your email"
              />
              <Form.Text className="text-muted">
                We'll never share your email with anyone else.
              </Form.Text>
            </Form.Group>
            
            <Form.Group className="mb-3" controlId="dateOfBirth">
              <Form.Label>Date of Birth</Form.Label>
              <Form.Control
                type="date"
                name="date_of_birth"
                value={formData.date_of_birth}
                onChange={handleChange}
                required
              />
            </Form.Group>
            
            <Form.Group className="mb-3" controlId="yearsOfExperience">
              <Form.Label>Years of Experience</Form.Label>
              <Form.Control
                type="number"
                name="years_of_experience"
                value={formData.years_of_experience}
                onChange={handleChange}
                required
                min="0"
                placeholder="Enter your years of experience"
              />
            </Form.Group>
            
            <Form.Group className="mb-3" controlId="department">
              <Form.Label>Department</Form.Label>
              <Form.Select
                name="department"
                value={formData.department}
                onChange={handleChange}
                required
              >
                <option value="">Select a department</option>
                <option value="IT">IT</option>
                <option value="HR">HR</option>
                <option value="FINANCE">Finance</option>
              </Form.Select>
            </Form.Group>
            
            <Form.Group className="mb-3" controlId="resume">
              <Form.Label>Resume</Form.Label>
              <Form.Control
                type="file"
                name="resume"
                onChange={handleFileChange}
                required
                accept=".pdf,.docx"
              />
              <Form.Text className="text-muted">
                Upload your resume in PDF or DOCX format (max 5MB).
              </Form.Text>
            </Form.Group>
            
            <Button 
              variant="primary" 
              type="submit" 
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Application'}
            </Button>
          </Form>
        )}
      </Card.Body>
    </Card>
  );
};

export default CandidateRegistration;