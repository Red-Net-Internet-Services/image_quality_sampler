"""Entry point for image_quality_sampler."""
import logging
from multiprocessing import freeze_support
from image_quality_sampler.qt import main  # pragma: no cover

if __name__ == "__main__":  # pragma: no cover
    freeze_support()
    try:
        main()
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
