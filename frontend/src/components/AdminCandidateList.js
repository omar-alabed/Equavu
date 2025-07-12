import React, { useState, useEffect } from 'react';
import { Table, Card, Badge, Button, Form, Pagination, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import axios from 'axios';

const AdminCandidateList = () => {
  // State
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filter, setFilter] = useState('');
  
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
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };
  
  // Load candidates
  const loadCandidates = async (page = 1, departmentFilter = '') => {
    setLoading(true);
    setError(null);
    
    try {
      // Build URL with query parameters
      let url = `/api/admin/candidates/?page=${page}`;
      if (departmentFilter) {
        url += `&department=${departmentFilter}`;
      }
      
      const response = await axios.get(url, {
        headers: {
          'X-ADMIN': '1'
        }
      });
      
      setCandidates(response.data.results);
      setTotalPages(Math.ceil(response.data.count / 10)); // Assuming 10 items per page
    } catch (error) {
      console.error('Error loading candidates:', error);
      setError(
        error.response?.data?.detail || 
        'An error occurred while loading candidates. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };
  
  // Handle filter change
  const handleFilterChange = (e) => {
    setFilter(e.target.value);
    setCurrentPage(1); // Reset to first page when filter changes
    loadCandidates(1, e.target.value);
  };
  
  // Handle page change
  const handlePageChange = (page) => {
    setCurrentPage(page);
    loadCandidates(page, filter);
  };
  
  // Load candidates on component mount
  useEffect(() => {
    loadCandidates(currentPage, filter);
  }, []);
  
  // Generate pagination items
  const paginationItems = [];
  for (let number = 1; number <= totalPages; number++) {
    paginationItems.push(
      <Pagination.Item 
        key={number} 
        active={number === currentPage}
        onClick={() => handlePageChange(number)}
      >
        {number}
      </Pagination.Item>
    );
  }
  
  return (
    <Card className="mb-4">
      <Card.Header as="h5">Candidate Management</Card.Header>
      <Card.Body>
        <div className="d-flex justify-content-between mb-3">
          <Form.Group controlId="departmentFilter" style={{ width: '200px' }}>
            <Form.Select 
              value={filter} 
              onChange={handleFilterChange}
              aria-label="Filter by department"
            >
              <option value="">All Departments</option>
              <option value="IT">IT</option>
              <option value="HR">HR</option>
              <option value="FINANCE">Finance</option>
            </Form.Select>
          </Form.Group>
          
          <Button 
            variant="outline-secondary" 
            onClick={() => loadCandidates(currentPage, filter)}
          >
            Refresh
          </Button>
        </div>
        
        {error && (
          <Alert variant="danger">
            {error}
          </Alert>
        )}
        
        {loading ? (
          <div className="text-center my-5">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <p className="mt-2">Loading candidates...</p>
          </div>
        ) : candidates.length === 0 ? (
          <Alert variant="info">
            No candidates found. Try changing the filter or adding new candidates.
          </Alert>
        ) : (
          <>
            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Date of Birth</th>
                  <th>Experience</th>
                  <th>Department</th>
                  <th>Status</th>
                  <th>Applied On</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {candidates.map((candidate) => (
                  <tr key={candidate.id}>
                    <td>{candidate.full_name}</td>
                    <td>{formatDate(candidate.date_of_birth)}</td>
                    <td>{candidate.years_of_experience} years</td>
                    <td>{candidate.department_display}</td>
                    <td>
                      <Badge bg={getStatusVariant(candidate.current_status)}>
                        {candidate.current_status_display}
                      </Badge>
                    </td>
                    <td>{formatDate(candidate.created_at)}</td>
                    <td>
                      <Link 
                        to={`/admin/candidates/${candidate.id}`} 
                        className="btn btn-sm btn-primary me-1"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
            
            <div className="d-flex justify-content-center mt-4">
              <Pagination>
                <Pagination.First 
                  onClick={() => handlePageChange(1)} 
                  disabled={currentPage === 1}
                />
                <Pagination.Prev 
                  onClick={() => handlePageChange(currentPage - 1)} 
                  disabled={currentPage === 1}
                />
                
                {paginationItems}
                
                <Pagination.Next 
                  onClick={() => handlePageChange(currentPage + 1)} 
                  disabled={currentPage === totalPages}
                />
                <Pagination.Last 
                  onClick={() => handlePageChange(totalPages)} 
                  disabled={currentPage === totalPages}
                />
              </Pagination>
            </div>
          </>
        )}
      </Card.Body>
    </Card>
  );
};

export default AdminCandidateList;