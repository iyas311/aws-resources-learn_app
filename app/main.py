from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi import Depends
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import HTMLResponse
from sqlalchemy.orm import Session
import os

from app.aws.s3 import upload_file, delete_object, list_files, get_object, generate_presigned_url
from app.aws.sns import publish_message
from app.aws.cloudwatch import logger
from app.aws.metrics import put_metric
from app.database import init_db, get_db
from app.models import Course

app = FastAPI(
    title="CloudLearn"
)

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Initialize database on startup
@app.on_event("startup")
def startup():
    init_db()

# Mount static files if they exist
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health():

    put_metric("HealthChecks")

    return {
        "status": "healthy"
    }


@app.post("/upload")
async def upload(
        file: UploadFile = File(...)
):

    try:
        upload_file(
            file.file,
            file.filename
        )

        logger.info(
            f"Uploaded file {file.filename}"
        )

        put_metric("Uploads")

        return {
            "message": "File Uploaded"
        }
    except Exception as e:
        put_metric("Errors")
        logger.error(f"Upload failed: {str(e)}")
        raise


@app.get("/notify")
def notify():

    try:
        publish_message(
            "CloudLearn",
            "Test SNS Notification"
        )

        logger.info(
            "SNS Notification Sent"
        )

        put_metric("Notifications")

        return {
            "message": "SNS Sent"
        }
    except Exception as e:
        put_metric("Errors")
        logger.error(f"Notification failed: {str(e)}")
        raise


@app.get("/files")
def files():

    return {
        "files": list_files()
    }


@app.get("/view/{filename}")
def view_file(filename: str):

    obj = get_object(filename)

    return StreamingResponse(
        obj["Body"],
        media_type=obj["ContentType"]
    )


@app.get("/view-url/{filename}")
def view_url(filename: str):

    return {
        "url": generate_presigned_url(filename)
    }


@app.get("/log")
def log_test():

    logger.info(
        "CloudWatch Test Log"
    )

    return {
        "message": "Log Created"
    }


# ============= TEMPLATE ROUTES =============

@app.get("/courses", response_class=HTMLResponse)
async def courses_page(request: Request):
    return templates.TemplateResponse("courses.html", {"request": request})


@app.get("/upload-course", response_class=HTMLResponse)
async def upload_course_page(request: Request):
    return templates.TemplateResponse("upload-course.html", {"request": request})


@app.get("/upload", response_class=HTMLResponse)
async def upload_alias(request: Request):
    return templates.TemplateResponse("upload-course.html", {"request": request})


@app.get("/course/{course_id}", response_class=HTMLResponse)
async def course_detail_page(request: Request, course_id: int):
    return templates.TemplateResponse("course-detail.html", {"request": request})


@app.get("/metrics", response_class=HTMLResponse)
async def metrics_page(request: Request):
    return templates.TemplateResponse("metrics.html", {"request": request})


@app.get("/files-page", response_class=HTMLResponse)
async def files_page(request: Request):
    return templates.TemplateResponse("files.html", {"request": request})


# ============= API ROUTES =============

@app.get("/api/courses")
def get_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    
    return {
        "courses": [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "instructor": course.instructor,
                "thumbnail": generate_presigned_url(course.thumbnail) if course.thumbnail else None,
            }
            for course in courses
        ]
    }


@app.get("/api/course/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        return {"error": "Course not found"}, 404
    
    return {
        "course": {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "instructor": course.instructor,
            "material": course.material,
            "material_name": course.material_name,
            "material_url": generate_presigned_url(course.material),
            "thumbnail": generate_presigned_url(course.thumbnail) if course.thumbnail else None,
            "created_at": course.created_at.isoformat() if course.created_at else None
        }
    }


@app.delete("/api/course/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return {"detail": "Course not found"}, 404

    # Delete S3 objects if they exist
    try:
        if course.thumbnail:
            delete_object(course.thumbnail)
        delete_object(course.material)
    except Exception as err:
        logger.error(f"Failed to delete S3 objects for course {course_id}: {err}")

    db.delete(course)
    db.commit()

    put_metric("Deletes")
    logger.info(f"Course deleted: {course_id}")

    return {"success": True}


@app.post("/api/upload-course")
async def upload_course(
    title: str = None,
    description: str = None,
    instructor: str = None,
    thumbnail: UploadFile = None,
    material: UploadFile = None,
    db: Session = Depends(get_db)
):
    try:
        # Validate required fields
        if not title or not description or not instructor or not material:
            return {"detail": "Missing required fields"}, 400

        # Generate unique filenames
        material_filename = f"material_{title.replace(' ', '_')}_{material.filename}"
        upload_file(material.file, material_filename)
        logger.info(f"Course material uploaded: {material_filename}")

        # Upload thumbnail if provided
        thumbnail_filename = None
        if thumbnail and thumbnail.filename:
            thumbnail_filename = f"thumbnail_{title.replace(' ', '_')}_{thumbnail.filename}"
            upload_file(thumbnail.file, thumbnail_filename)
            logger.info(f"Course thumbnail uploaded: {thumbnail_filename}")

        # Create course in database
        new_course = Course(
            title=title,
            description=description,
            instructor=instructor,
            material=material_filename,
            material_name=material.filename,
            thumbnail=thumbnail_filename
        )
        
        db.add(new_course)
        db.commit()
        db.refresh(new_course)

        # Record metrics
        put_metric("Uploads")
        
        logger.info(f"Course created: {title}")

        return {"success": True, "course_id": new_course.id}

    except Exception as e:
        db.rollback()
        put_metric("Errors")
        logger.error(f"Course upload failed: {str(e)}")
        return {"detail": str(e)}, 500