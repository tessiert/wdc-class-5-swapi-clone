import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.models import Planet, People
from api.fixtures import SINGLE_PEOPLE_OBJECT, PEOPLE_OBJECTS
from api.serializers import serialize_people_as_json


def single_people(request):
    return JsonResponse(SINGLE_PEOPLE_OBJECT)


def list_people(request):
    return JsonResponse(PEOPLE_OBJECTS, safe=False)


@csrf_exempt
def people_list_view(request):
    """
    People `list` actions:

    Based on the request method, perform the following actions:

        * GET: Return the list of all `People` objects in the database.

        * POST: Create a new `People` object using the submitted JSON payload.

    Make sure you add at least these validations:

        * If the view receives another HTTP method out of the ones listed
          above, return a `400` response.

        * If submited payload is not JSON valid, return a `400` response.
    """
    # Test for valid JSON and type check
    if request.body:
        try:
            payload = json.loads(request.body)
            if (not isinstance(payload['height'], int) or not isinstance(payload['mass'], int) 
                or not isinstance(payload['homeworld'], int)):
                return JsonResponse({"msg": "Provided payload is not valid", "success": False}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'msg': 'Provide a valid JSON payload', 'success': False}, status=400)

    # GET will return a list of all people and POST will create a new person
    # All other methods are forbidden
    if (request.method == 'GET'):
        people = [serialize_people_as_json(person) for person in People.objects.all()]
        return JsonResponse(people, safe=False)
    elif (request.method == 'POST'):
        homeworld_id = payload['homeworld']
        try:
            homeworld = Planet.objects.get(id=homeworld_id)
        except Planet.DoesNotExist:
            return JsonResponse({
                "success": False,
                "msg": "Could not find planet with id: {}".format(homeworld_id)
            }, status=404)
        new_person = People({
            'name': payload['name'],
            'homeworld': 'http://localhost:8000/planets/{}/'.format(payload['homeworld']),
            'height': payload['height'],
            'mass': payload['mass'],
            'hair_color': payload['hair_color']
        })
        new_person.save()
    else:
        return JsonResponse({'msg': 'Invalid HTTP method', 'success': False}, status=400)


@csrf_exempt
def people_detail_view(request, people_id):
    """
    People `detail` actions:

    Based on the request method, perform the following actions:

        * GET: Returns the `People` object with given `people_id`.

        * PUT/PATCH: Updates the `People` object either partially (PATCH)
          or completely (PUT) using the submitted JSON payload.

        * DELETE: Deletes `People` object with given `people_id`.

    Make sure you add at least these validations:

        * If the view receives another HTTP method out of the ones listed
          above, return a `400` response.

        * If submited payload is nos JSON valid, return a `400` response.
    """
    # Test for valid JSON and type check
    if request.body:
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'msg': 'Provide a valid JSON payload', 'success': False}, status=400)
        if (not isinstance(payload['height'], int) or not isinstance(payload['mass'], int) 
            or not isinstance(payload['homeworld'], int)):
            return JsonResponse({"msg": "Provided payload is not valid", "success": False}, status=400)

    # Find the specified person, or return an error if not found
    try:
        queried_person = People.objects.get(id=people_id)
        json_person = serialize_people_as_json(queried_person)
    except People.DoesNotExist:
        return JsonResponse({"msg": "Requested person not found", "success": False}, status=404)

    # Process the HTTP request
    if (request.method == 'GET'):
        return JsonResponse(json_person, safe=False)
    elif (request.method in ['PUT', 'PATCH']):
        for field in payload:
            json_person.field = payload['field']
        json_person.save()
    elif (request.method == 'DELETE'):
        delete_response = queried_person.delete()
        if delete_response[0] > 0:
            return JsonResponse({'success': True}, status=200)
        else:
            return JsonResponse({'Delete Failed': 'Unknown error'}, status=500)
    else:
        return JsonResponse({'msg': 'Invalid HTTP method', 'success': False}, status=400)


