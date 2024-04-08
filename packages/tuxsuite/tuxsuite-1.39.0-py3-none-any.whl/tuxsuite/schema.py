# -*- coding: utf-8 -*-

import re
from voluptuous import Any, Optional, Required, Schema, Url, Invalid, All

SchemaError = Invalid


def plan():
    return Schema(
        {
            Required("version"): 1,
            Optional("name"): str,
            Optional("description"): str,
            Required("jobs"): [
                Any(
                    Schema(
                        {
                            Optional("name"): str,
                            Required("build"): dict,
                            Optional("sanity_test"): dict,
                        }
                    ),
                    Schema(
                        {
                            Optional("name"): str,
                            Required("build"): dict,
                            Required("test"): dict,
                            Optional("sanity_test"): dict,
                        }
                    ),
                    Schema(
                        {
                            Optional("name"): str,
                            Required("build"): dict,
                            Required("tests"): list,
                            Optional("sanity_test"): dict,
                        }
                    ),
                    Schema(
                        {
                            Optional("name"): str,
                            Required("builds"): list,
                            Optional("sanity_test"): dict,
                        }
                    ),
                    Schema(
                        {
                            Optional("name"): str,
                            Required("builds"): list,
                            Required("test"): dict,
                            Optional("sanity_test"): dict,
                        }
                    ),
                    Schema(
                        {
                            Optional("name"): str,
                            Required("builds"): list,
                            Required("tests"): list,
                            Optional("sanity_test"): dict,
                        }
                    ),
                    Schema(
                        {
                            Optional("name"): str,
                            Optional("sanity_test"): dict,
                            Required("tests"): list,
                        }
                    ),
                    Schema(
                        {
                            Optional("name"): str,
                            Required("test"): dict,
                            Optional("sanity_test"): dict,
                        }
                    ),
                )
            ],
        },
        extra=True,
    )


def bake_plan():
    return Schema(
        {
            Optional("common"): dict,
            Required("version"): 1,
            Optional("name"): str,
            Optional("description"): str,
            Required("jobs"): [
                Any(
                    Schema({Optional("name"): str, Required("bake"): dict}),
                    Schema(
                        {
                            Optional("name"): str,
                            Required("bake"): dict,
                            Required("test"): dict,
                        }
                    ),
                    Schema(
                        {
                            Optional("name"): str,
                            Required("bake"): dict,
                            Required("tests"): list,
                        }
                    ),
                    Schema({Optional("name"): str, Required("bakes"): list}),
                    Schema(
                        {
                            Optional("name"): str,
                            Required("bakes"): list,
                            Required("test"): dict,
                        }
                    ),
                    Schema(
                        {
                            Optional("name"): str,
                            Required("bakes"): list,
                            Required("tests"): list,
                        }
                    ),
                    Schema(
                        {
                            Optional("name"): str,
                            Required("tests"): list,
                        }
                    ),
                    Schema({Optional("name"): str, Required("test"): dict}),
                )
            ],
        },
        extra=True,
    )


def validate_git_url(url):
    git_url_pattern = r"^(https?|git)://"
    if not re.match(git_url_pattern, url):
        raise Invalid("Invalid url")
    return url


def validate_git_ref(git_ref):
    if len(git_ref) > 128:
        raise Invalid(f"branch (git_ref): {git_ref} too long: {len(git_ref)} chars")
    git_ref_re = re.compile(r"^[/\w_.-]+$")
    if not re.match(git_ref_re, git_ref):
        raise Invalid(f"branch name: {git_ref}, must be a valid git_ref")
    return git_ref


def tuxtrigger_config():
    return Schema(
        {
            Required("repositories"): [
                {
                    Optional("branches"): [
                        {
                            Required("name"): All(str, validate_git_ref),
                            Required("plan"): str,
                            Optional("squad_project"): str,
                            Optional("lab"): str,
                            Optional("lava_test_plans_project"): str,
                        }
                    ],
                    Required("url"): All(Url(), validate_git_url),
                    Required("squad_group"): str,
                    Optional("regex"): str,
                    Optional("default_plan"): str,
                    Optional("default_squad_project"): str,
                    Optional("squad_project_prefix"): str,
                    Optional("lab"): str,
                    Optional("lava_test_plans_project"): str,
                }
            ]
        }
    )
