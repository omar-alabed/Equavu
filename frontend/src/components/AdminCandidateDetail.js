import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Badge, Button, Form, ListGroup, Alert, Row, Col, Modal } from 'react-bootstrap';
import axios from 'axios';

const AdminCandidateDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  // State
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Status update state
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [statusData, setStatusData] = useState({
    status: '',
    feedback: ''
  });
  const [updating, setUpdating] = useState(false);
  const [updateError, setUpdateError] = useState(null);
  
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
  
  // Load candidate details
  const loadCandidate = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/admin/candidates/${id}/`, {
        headers: {
          'X-ADMIN': '1'
        }
      });
      
      setCandidate(response.data);
      // Initialize status form with current status
      setStatusData({
        status: response.data.current_status,
        feedback: ''
      });
    } catch (error) {
      console.error('Error loading candidate details:', error);
      setError(
        error.response?.data?.detail || 
        'An error occurred while loading candidate details. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };
  
  // Download resume
  const downloadResume = async () => {
    try {
      const response = await axios.get(`/api/admin/candidates/${id}/resume/`, {
        headers: {
          'X-ADMIN': '1'
        },
        responseType: 'blob'
      });
      
      // Create a URL for the blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Get filename from Content-Disposition header or use a default
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'resume.pdf';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch.length === 2) {
          filename = filenameMatch[1];
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading resume:', error);
      alert('Error downloading resume. Please try again.');
    }
  };
  
  // Handle status form input changes
  const handleStatusChange = (e) => {
    const { name, value } = e.target;
    setStatusData({
      ...statusData,
      [name]: value
    });
  };
  
  // Update candidate status
  const updateStatus = async () => {
    setUpdating(true);
    setUpdateError(null);
    
    try {
      await axios.put(
        `/api/admin/candidates/${id}/status/`,
        statusData,
        {
          headers: {
            'X-ADMIN': '1',
            'X-ADMIN-USER': 'Admin User' // In a real app, this would be the logged-in admin's name
          }
        }
      );
      
      // Reload candidate data
      await loadCandidate();
      
      // Close modal
      setShowStatusModal(false);
      
      // Reset form
      setStatusData({
        status: candidate.current_status,
        feedback: ''
      });
    } catch (error) {
      console.error('Error updating status:', error);
      setUpdateError(
        error.response?.data?.detail || 
        'An error occurred while updating the status. Please try again.'
      );
    } finally {
      setUpdating(false);
    }
  };
  
  // Load candidate on component mount
  useEffect(() => {
    loadCandidate();
  }, [id]);
  
  if (loading) {
    return (
      <div className="text-center my-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="mt-2">Loading candidate details...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error</Alert.Heading>
        <p>{error}</p>
        <Button variant="outline-danger" onClick={() => navigate('/admin/candidates')}>
          Back to Candidates
        </Button>
      </Alert>
    );
  }
  
  if (!candidate) {
    return (
      <Alert variant="warning">
        <Alert.Heading>Candidate Not Found</Alert.Heading>
        <p>The candidate you are looking for does not exist or has been removed.</p>
        <Button variant="outline-primary" onClick={() => navigate('/admin/candidates')}>
          Back to Candidates
        </Button>
      </Alert>
    );
  }
  
  return (
    <>
      <Card className="mb-4">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Candidate Details</h5>
          <div>
            <Button 
              variant="outline-primary" 
              className="me-2"
              onClick={() => navigate('/admin/candidates')}
            >
              Back to List
            </Button>
            <Button 
              variant="primary"
              onClick={() => setShowStatusModal(true)}
            >
              Update Status
            </Button>
          </div>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={6}>
              <h6>Personal Information</h6>
              <ListGroup variant="flush" className="mb-4">
                <ListGroup.Item>
                  <strong>Name:</strong> {candidate.full_name}
                </ListGroup.Item>
                <ListGroup.Item>
                  <strong>Email:</strong> {candidate.email}
                </ListGroup.Item>
                <ListGroup.Item>
                  <strong>Date of Birth:</strong> {formatDate(candidate.date_of_birth)}
                </ListGroup.Item>
                <ListGroup.Item>
                  <strong>Years of Experience:</strong> {candidate.years_of_experience}
                </ListGroup.Item>
                <ListGroup.Item>
                  <strong>Department:</strong> {candidate.department_display}
                </ListGroup.Item>
                <ListGroup.Item>
                  <strong>Resume:</strong>{' '}
                  <Button 
                    variant="link" 
                    className="p-0" 
                    onClick={downloadResume}
                  >
                    Download Resume
                  </Button>
                </ListGroup.Item>
              </ListGroup>
            </Col>
            
            <Col md={6}>
              <h6>Application Status</h6>
              <ListGroup variant="flush" className="mb-4">
                <ListGroup.Item>
                  <strong>Current Status:</strong>{' '}
                  <Badge bg={getStatusVariant(candidate.current_status)}>
                    {candidate.current_status_display}
                  </Badge>
                </ListGroup.Item>
                <ListGroup.Item>
                  <strong>Application Date:</strong> {formatDate(candidate.created_at)}
                </ListGroup.Item>
                <ListGroup.Item>
                  <strong>Last Updated:</strong> {formatDate(candidate.updated_at)}
                </ListGroup.Item>
              </ListGroup>
            </Col>
          </Row>
          
          <h6>Status History</h6>
          <ListGroup variant="flush">
            {candidate.status_changes.map((statusChange) => (
              <ListGroup.Item key={statusChange.id}>
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <Badge bg={getStatusVariant(statusChange.new_status)}>
                      {statusChange.new_status.replace('_', ' ')}
                    </Badge>
                    {statusChange.previous_status && (
                      <small className="text-muted ms-2">
                        (from {statusChange.previous_status.replace('_', ' ')})
                      </small>
                    )}
                    {statusChange.feedback && (
                      <p className="mt-2 mb-0">{statusChange.feedback}</p>
                    )}
                    {statusChange.admin_user && (
                      <small className="text-muted d-block mt-1">
                        Updated by: {statusChange.admin_user}
                      </small>
                    )}
                  </div>
                  <small className="text-muted">
                    {formatDate(statusChange.created_at)}
                  </small>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </Card.Body>
      </Card>
      
      {/* Status Update Modal */}
      <Modal show={showStatusModal} onHide={() => setShowStatusModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Update Application Status</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {updateError && (
            <Alert variant="danger">
              {updateError}
            </Alert>
          )}
          
          <Form>
            <Form.Group className="mb-3" controlId="status">
              <Form.Label>Status</Form.Label>
              <Form.Select
                name="status"
                value={statusData.status}
                onChange={handleStatusChange}
                required
              >
                <option value="SUBMITTED">Submitted</option>
                <option value="UNDER_REVIEW">Under Review</option>
                <option value="INTERVIEW_SCHEDULED">Interview Scheduled</option>
                <option value="ACCEPTED">Accepted</option>
                <option value="REJECTED">Rejected</option>
              </Form.Select>
            </Form.Group>
            
            <Form.Group className="mb-3" controlId="feedback">
              <Form.Label>Feedback</Form.Label>
              <Form.Control
                as="textarea"
                name="feedback"
                value={statusData.feedback}
                onChange={handleStatusChange}
                rows={3}
                placeholder="Enter feedback for the candidate"
              />
              <Form.Text className="text-muted">
                This feedback will be visible to the candidate.
              </Form.Text>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowStatusModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={updateStatus}
            disabled={updating}
          >
            {updating ? 'Updating...' : 'Update Status'}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default AdminCandidateDetail;