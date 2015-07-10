#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 theiconic.com.au development@theiconic.com.au

from os.path import join, expanduser
from thumbor.utils import logger
from tornado.concurrent import return_future
import pyrax

CONNECTIONS = {}

@return_future
def load(context, path, callback):
    key = (
            context.config.RACKSPACE_PYRAX_REGION, 
            context.config.get('RACKSPACE_PYRAX_IDENTITY_TYPE','rackspace'),
            context.config.RACKSPACE_PYRAX_CFG,
            context.config.RACKSPACE_PYRAX_PUBLIC,
            context.config.RACKSPACE_LOADER_CONTAINER
        )

    if key not in CONNECTIONS:
        if(context.config.RACKSPACE_PYRAX_REGION):
            pyrax.set_default_region(context.config.RACKSPACE_PYRAX_REGION)
        pyrax.set_setting('identity_type', context.config.get('RACKSPACE_PYRAX_IDENTITY_TYPE','rackspace'))
        pyrax.set_credential_file(expanduser(context.config.RACKSPACE_PYRAX_CFG))
        cf = pyrax.connect_to_cloudfiles(public=context.config.RACKSPACE_PYRAX_PUBLIC)
        CONNECTIONS[key] = cf.get_container(context.config.RACKSPACE_LOADER_CONTAINER)

    cont = CONNECTIONS[key]
    file_abspath = normalize_path(context, path)
    logger.debug("[LOADER] getting from %s/%s" % (context.config.RACKSPACE_LOADER_CONTAINER, file_abspath))
    try:
        obj = cont.get_object(file_abspath)
        if obj:
            logger.debug("[LOADER] Found object at %s/%s" % (context.config.RACKSPACE_LOADER_CONTAINER, file_abspath))
        else:
            logger.warning("[LOADER] Unable to find object %s/%s" % (context.config.RACKSPACE_LOADER_CONTAINER, file_abspath ))
    except:
        callback(None)
    else:
        callback(obj.get())


def normalize_path(context, path):
    path = join(context.config.RACKSPACE_LOADER_CONTAINER_ROOT.rstrip('/'), path.lstrip('/'))
    path = path.replace('http://', '')
    return path
