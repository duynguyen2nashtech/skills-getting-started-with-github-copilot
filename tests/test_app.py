import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a deep copy of the initial activities for resetting
initial_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities dictionary to its initial state before each test for isolation."""
    global activities
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))

client = TestClient(app)

def test_root_redirect():
    """Test that the root endpoint redirects to the static index.html."""
    # Arrange: No specific setup needed
    
    # Act: Make a GET request to the root endpoint (don't follow redirects)
    response = client.get("/", follow_redirects=False)
    
    # Assert: Check for redirect status and location
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test retrieving all activities."""
    # Arrange: Activities are already set up via fixture
    
    # Act: Make a GET request to /activities
    response = client.get("/activities")
    
    # Assert: Check status and response data
    assert response.status_code == 200
    assert response.json() == activities

def test_signup_success():
    """Test successful signup for an activity."""
    # Arrange: Choose an activity and a new email
    activity = "Chess Club"
    email = "new@student.edu"
    
    # Act: Make a POST request to signup
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert: Check success status and message
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]

def test_signup_activity_not_found():
    """Test signup for a non-existent activity."""
    # Arrange: Use a non-existent activity name
    activity = "NonExistent Club"
    email = "student@mergington.edu"
    
    # Act: Attempt to signup
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert: Check for 404 error
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_signup_already_signed_up():
    """Test signup when student is already signed up."""
    # Arrange: Use an activity and an email already in participants
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already in the list
    
    # Act: Attempt to signup again
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert: Check for 400 error
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}

def test_unregister_success():
    """Test successful unregistration from an activity."""
    # Arrange: Choose an activity and an existing participant
    activity = "Chess Club"
    email = "michael@mergington.edu"
    
    # Act: Make a DELETE request to unregister
    response = client.delete(f"/activities/{activity}/participants/{email}")
    
    # Assert: Check success status and message
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    assert email not in activities[activity]["participants"]

def test_unregister_activity_not_found():
    """Test unregistration from a non-existent activity."""
    # Arrange: Use a non-existent activity
    activity = "NonExistent Club"
    email = "student@mergington.edu"
    
    # Act: Attempt to unregister
    response = client.delete(f"/activities/{activity}/participants/{email}")
    
    # Assert: Check for 404 error
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_unregister_participant_not_found():
    """Test unregistration when participant is not signed up."""
    # Arrange: Use an activity and an email not in participants
    activity = "Chess Club"
    email = "notsigned@mergington.edu"
    
    # Act: Attempt to unregister
    response = client.delete(f"/activities/{activity}/participants/{email}")
    
    # Assert: Check for 404 error
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}