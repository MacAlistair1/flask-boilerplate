from flask import request, jsonify
from os import environ
from src.constants.http_status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND


def paginator_service(paginate, items):
    links = {
        "first": environ.get('FLASK_URL') + request.path+"?currentPage=1",
        "last": environ.get('FLASK_URL') + request.path+"?currentPage="+str(paginate.pages),
        "prev": environ.get('FLASK_URL') + request.path+"?currentPage="+str(paginate.prev_num) if paginate.prev_num != 0 else "",
        "next": environ.get('FLASK_URL') + request.path+"?currentPage="+str(paginate.next_num) if paginate.page < paginate.pages else "",
    }

    meta = {
        "currentPage": paginate.page,
        "from": 1,
        "lastPage": paginate.pages,
        "path": environ.get('FLASK_URL') + request.path,
        "per_page": paginate.per_page,
        "to": paginate.pages,
        "total": paginate.total
    },

    return withDataMetaResponse(items, meta, links)


def errorResponse(message="", code=HTTP_404_NOT_FOUND):
    return jsonify({
        "status": False,
        "statusCode": code,
        "message": message,
    }), code


def successResponse(message="", code=HTTP_200_OK):
    return jsonify({
        "status": True,
        "statusCode": code,
        "message": message,
    }), code


def withDataResponse(data=None, message="", code=HTTP_200_OK):
    return jsonify({
        "status": True,
        "data": data,
        "statusCode": code,
        "message": message,
    }), code


def withDataMetaResponse(data=None, meta=None, links=None, message="", code=HTTP_200_OK):
    return jsonify({
        "status": True,
        "data": data,
        "meta": meta,
        "links": links,
        "statusCode": code,
        "message": message,
    }), code
