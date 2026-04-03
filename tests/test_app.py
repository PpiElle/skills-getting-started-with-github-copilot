import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before and after each test"""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities(self, client, reset_activities):
        """
        Arrange: Initialize test client
        Act: Send GET request to /activities
        Assert: Verify response status 200 and all activities are returned
        """
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class", 
                              "Basketball Team", "Soccer Club", "Art Club", 
                              "Drama Club", "Debate Club", "Science Club"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert all(activity in data for activity in expected_activities)
        assert len(data) == 9


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity(self, client, reset_activities):
        """
        Arrange: Select an activity with empty participants (Basketball Team)
        Act: Sign up a new participant
        Assert: Verify response 200, message returned, and participant added to activity
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added by fetching activities
        activities_resp = client.get("/activities")
        assert email in activities_resp.json()[activity_name]["participants"]

    def test_signup_duplicate_email(self, client, reset_activities):
        """
        Arrange: Select activity with existing participant (Chess Club)
        Act: Attempt to sign up same participant twice
        Assert: First succeeds (200), second fails (400) with duplicate error
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act & Assert - Second signup should fail
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == 400
        assert "già registrato" in response.json()["detail"]

    def test_signup_activity_not_found(self, client, reset_activities):
        """
        Arrange: Prepare invalid activity name
        Act: Attempt to sign up for non-existent activity
        Assert: Verify 404 response with Activity not found detail
        """
        # Arrange
        invalid_activity = "NonExistent Club"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_remove_participant(self, client, reset_activities):
        """
        Arrange: Select activity with existing participant (Chess Club)
        Act: Delete that participant
        Assert: Verify 200 response and participant removed from activity list
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email_to_remove}
        )

        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant was removed
        activities_resp = client.get("/activities")
        assert email_to_remove not in activities_resp.json()[activity_name]["participants"]

    def test_remove_participant_not_found(self, client, reset_activities):
        """
        Arrange: Prepare email not in any activity participants
        Act: Attempt to remove non-existent participant
        Assert: Verify 404 response with Participant not found detail
        """
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "nobody@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": nonexistent_email}
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_participant_activity_not_found(self, client, reset_activities):
        """
        Arrange: Prepare invalid activity name
        Act: Attempt to remove participant from non-existent activity
        Assert: Verify 404 response with Activity not found detail
        """
        # Arrange
        invalid_activity = "NonExistent Club"
        email = "test@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
