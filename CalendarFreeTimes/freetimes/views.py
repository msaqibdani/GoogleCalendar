from django.shortcuts import render
from django.http import HttpResponse
from . import quickstart as qp



# Create your views here.
def index(request):
	
	if request.method == "POST":
		#print(request.POST['start_date'], print(request.POST['end_date']))

		a = qp.CalendarFreeTimes()
		#print(a.from_date, a.to_date, a.SCOPES, a.ZONES, a.times, a.service, a.freeTimes, sep = '\n')

		a.setFromDate(request.POST['start_date'])
		a.setToDate(request.POST['end_date'])

		#print(a.from_date, a.to_date, a.SCOPES, a.ZONES, a.times, a.service, a.freeTimes, sep = '\n')

		a.main()
		print(a.freeTimes)
		#return HttpResponse(request.POST['start_date'] + ' \n' + request.POST['end_date'])
	return render(request, "freetimes/index.html")


def callback(request):
	return HttpResponse('Authentication complete!')