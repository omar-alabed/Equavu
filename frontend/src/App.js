import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Container, Navbar, Nav } from 'react-bootstrap';
import './App.css';

// Import components
import CandidateRegistration from './components/CandidateRegistration';
import CandidateStatus from './components/CandidateStatus';
import AdminCandidateList from './components/AdminCandidateList';
import AdminCandidateDetail from './components/AdminCandidateDetail';

function App() {
  // State to track if admin mode is active
  const [isAdmin, setIsAdmin] = React.useState(false);

  // Toggle admin mode
  const toggleAdminMode = () => {
    setIsAdmin(!isAdmin);
  };

  return (
    <Router>
      <div className="App">
        <Navbar bg="dark" variant="dark" expand="lg">
          <Container>
            <Navbar.Brand as={Link} to="/">Equavo HR System</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="me-auto">
                <Nav.Link as={Link} to="/">Home</Nav.Link>
                <Nav.Link as={Link} to="/register">Register</Nav.Link>
                <Nav.Link as={Link} to="/status">Check Status</Nav.Link>
                {isAdmin && (
                  <Nav.Link as={Link} to="/admin/candidates">Admin: Candidates</Nav.Link>
                )}
              </Nav>
              <Nav>
                <Nav.Link onClick={toggleAdminMode}>
                  {isAdmin ? 'Exit Admin Mode' : 'Admin Mode'}
                </Nav.Link>
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        <Container className="mt-4">
          <Routes>
            <Route path="/" element={
              <div className="jumbotron">
                <h1>Welcome to Equavo HR System</h1>
                <p>
                  A minimal HR system allowing job applicants to register as candidates and upload their resumes,
                  while HR managers can log in, view the list of candidates, and download their resumes.
                </p>
                <hr />
                <p>
                  <Link to="/register" className="btn btn-primary me-2">Register as Candidate</Link>
                  <Link to="/status" className="btn btn-secondary me-2">Check Application Status</Link>
                  {isAdmin && (
                    <Link to="/admin/candidates" className="btn btn-danger">Admin: View Candidates</Link>
                  )}
                </p>
              </div>
            } />
            <Route path="/register" element={<CandidateRegistration />} />
            <Route path="/status" element={<CandidateStatus />} />

            {/* Admin routes */}
            {isAdmin && (
              <>
                <Route path="/admin/candidates" element={<AdminCandidateList />} />
                <Route path="/admin/candidates/:id" element={<AdminCandidateDetail />} />
              </>
            )}

            {/* Catch-all route for 404 */}
            <Route path="*" element={
              <div className="text-center mt-5">
                <h2>404 - Page Not Found</h2>
                <p>The page you are looking for does not exist.</p>
                <Link to="/" className="btn btn-primary">Go Home</Link>
              </div>
            } />
          </Routes>
        </Container>

        <footer className="footer mt-auto py-3 bg-light">
          <Container className="text-center">
            <span className="text-muted">Equavo HR System &copy; 2025</span>
          </Container>
        </footer>
      </div>
    </Router>
  );
}

export default App;