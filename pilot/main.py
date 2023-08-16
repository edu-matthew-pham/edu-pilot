# main.py
from __future__ import print_function, unicode_literals

from dotenv import load_dotenv
load_dotenv()

from helpers.Project import Project

from utils.arguments import get_arguments
from logger.logger import logger


def init():
    arguments = get_arguments()

    logger.info(f"Starting with args: {arguments}")

    return arguments


if __name__ == "__main__":
    args = init()

    # TODO get checkpoint from database and fill the project with it
    project = Project(args)
    project.start()