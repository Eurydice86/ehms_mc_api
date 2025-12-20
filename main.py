"""
Cloud Functions entry point for EHMS MyClub API pipeline.
This function is triggered by Cloud Scheduler to run the data pipeline daily.
"""
import functions_framework
from src import initialise
from src.logger import log, error
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


@functions_framework.http
def run_pipeline(request):
    """
    HTTP Cloud Function entry point.

    Args:
        request (flask.Request): The request object.

    Returns:
        Response tuple with message and status code
    """
    try:
        log("Starting EHMS MyClub API pipeline...")

        # Get optional interval parameter from request (default 60 days)
        interval = 60
        if request.args and 'interval' in request.args:
            try:
                interval = int(request.args.get('interval'))
                log(f"Using custom interval: {interval} days")
            except ValueError:
                log(f"Invalid interval parameter, using default: {interval} days")

        # Run the pipeline
        initialise.run(interval=interval)

        log("Pipeline completed successfully!")
        return {'status': 'success', 'message': 'Pipeline executed successfully'}, 200

    except Exception as e:
        error_msg = f"Pipeline failed: {str(e)}"
        error(error_msg)
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'message': error_msg}, 500


@functions_framework.cloud_event
def run_pipeline_cloud_event(cloud_event):
    """
    CloudEvent function entry point (alternative trigger type).

    Args:
        cloud_event: The CloudEvent that triggered this function.

    Returns:
        None
    """
    try:
        log("Starting EHMS MyClub API pipeline (CloudEvent trigger)...")
        initialise.run(interval=60)
        log("Pipeline completed successfully!")
    except Exception as e:
        error_msg = f"Pipeline failed: {str(e)}"
        error(error_msg)
        import traceback
        traceback.print_exc()
        raise
