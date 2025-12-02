import pytest
from shared.schemas.job import JobRequest

def test_job_request_creation():
    job = JobRequest(video_url="http://example.com", user_id="user_1")
    assert job.video_url == "http://example.com"
    assert job.user_id == "user_1"
    assert job.preset == "default"
    assert job.options == {}

def test_job_request_custom_preset():
    job = JobRequest(video_url="url", user_id="user_1", preset="detailed")
    assert job.preset == "detailed"

def test_job_request_custom_options():
    job = JobRequest(video_url="url", user_id="user_1", options={"lang": "ja"})
    assert job.options == {"lang": "ja"}

def test_job_request_missing_url():
    with pytest.raises(Exception):
        JobRequest(user_id="user_1")

def test_job_request_missing_user_id():
    with pytest.raises(Exception):
        JobRequest(video_url="url")

def test_job_request_dict_conversion():
    job = JobRequest(video_url="url", user_id="user_1")
    data = job.model_dump()
    assert data["video_url"] == "url"
    assert data["user_id"] == "user_1"

def test_job_request_json_conversion():
    job = JobRequest(video_url="url", user_id="user_1")
    json_str = job.model_dump_json()
    assert "url" in json_str
    assert "user_1" in json_str

def test_job_request_extra_fields():
    # Pydantic ignores extra fields by default unless configured otherwise
    job = JobRequest(video_url="url", user_id="user_1", extra="field")
    assert not hasattr(job, "extra")

def test_job_request_invalid_types():
    with pytest.raises(Exception):
        JobRequest(video_url=123, user_id="user_1") # Should be string, though pydantic might coerce

def test_job_request_empty_options():
    job = JobRequest(video_url="url", user_id="user_1", options={})
    assert job.options == {}
