from django.shortcuts import render

# Create your views here.


#vista principal
def principal(request):
	return render(request,'inicio.html')



# #vista cerrar_sesion
# def cerrar_sesion(request):
# 	user = request.user
# 	if user.is_authenticated():
# 		logout(request)
# 		return HttpResponseRedirect(reverse('sumacua_app:login'))
# 	else:
# 		return HttpResponseRedirect(reverse('sumacua_app:login'))

