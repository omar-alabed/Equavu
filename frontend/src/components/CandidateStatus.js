import React, { useState } from 'react';
import { Form, Button, Alert, Card, ListGroup, Badge } from 'react-bootstrap';
import axios from 'axios';

const CandidateStatus = () => {
  // Form state
  const [candidateId, setCandidateId] = useState('');
  
  // Status state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [candidateData, setCandidateData] = useState(null);
  
  // Handle input change
  const handleChange = (e) => {
    setCandidateId(e.target.value);
  };
  
  // Get status badge variant based on status
  const getStatusVariant = (status) => {
    switch (status) {
      case 'SUBMITTED':
        return 'primary';
      case 'UNDER_REVIEW':
        return 'info';
      case 'INTERVIEW_SCHEDULED':
        return 'warning';
      case 'ACCEPTED':
        return 'success';
      case 'REJECTED':
        return 'danger';
      default:
        return 'secondary';
    }
  };
  
  // Format date
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!candidateId.trim()) {
      setError('Please enter a candidate ID');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setCandidateData(null);
    
    try {
      const response = await axios.get(`/api/candidates/${candidateId}/status/`);
      setCandidateData(response.data);
    } catch (error) {
      console.error('Error fetching status:', error);
      setError(
        error.response?.data?.detail || 
        'An error occurred while fetching the application status. Please check your candidate ID and try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Card className="mb-4">
      <Card.Header as="h5">Check Application Status</Card.Header>
      <Card.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3" controlId="candidateId">
            <Form.Label>Candidate ID</Form.Label>
            <Form.Control
              type="text"
              value={candidateId}
              onChange={handleChange}
              placeholder="Enter your candidate ID"
              required
            />
            <Form.Text className="text-muted">
              Enter the ID you received after registration.
            </Form.Text>
          </Form.Group>
          
          <Button 
            variant="primary" 
            type="submit" 
            disabled={isLoading}
          >
            {isLoading ? 'Loading...' : 'Check Status'}
          </Button>
        </Form>
        
        {error && (
          <Alert variant="danger" className="mt-3">
            {error}
          </Alert>
        )}
        
        {candidateData && (
          <div className="mt-4">
            <Card>
              <Card.Header>
                <h5 className="mb-0">Application Details</h5>
              </Card.Header>
              <Card.Body>
                <div className="mb-3">
                  <strong>Name:</strong> {candidateData.full_name}
                </div>
                <div className="mb-3">
                  <strong>Email:</strong> {candidateData.email}
                </div>
                <div className="mb-3">
                  <strong>Department:</strong> {candidateData.department_display}
                </div>
                <div className="mb-3">
                  <strong>Current Status:</strong>{' '}
                  <Badge bg={getStatusVariant(candidateData.current_status)}>
                    {candidateData.current_status_display}
                  </Badge>
                </div>
                <div className="mb-3">
                  <strong>Application Date:</strong> {formatDate(candidateData.created_at)}
                </div>
                <div className="mb-3">
                  <strong>Last Updated:</strong> {formatDate(candidateData.updated_at)}
                </div>
              </Card.Body>
            </Card>
            
            <Card className="mt-3">
              <Card.Header>
                <h5 className="mb-0">Status History</h5>
              </Card.Header>
              <ListGroup variant="flush">
                {candidateData.status_changes.map((statusChange) => (
                  <ListGroup.Item key={statusChange.id}>
                    <div className="d-flex justify-content-between align-items-center">
                      <div>
                        <Badge bg={getStatusVariant(statusChange.new_status)}>
                          {statusChange.new_status.replace('_', ' ')}
                        </Badge>
                        {statusChange.feedback && (
                          <p className="mt-2 mb-0">{statusChange.feedback}</p>
                        )}
                      </div>
                      <small className="text-muted">
                        {formatDate(statusChange.created_at)}
                      </small>
                    </div>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </Card>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default CandidateStatus;