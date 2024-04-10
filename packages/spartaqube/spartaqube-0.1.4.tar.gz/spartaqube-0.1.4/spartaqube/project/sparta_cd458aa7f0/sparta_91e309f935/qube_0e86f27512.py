from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_0ed9d00fc8.sparta_3b136f3c7e.qube_316bac807a as qube_316bac807a
from project.sparta_25e81b3097.sparta_5f5d899812.qube_dc69199006 import sparta_7dc1413727
@csrf_exempt
@sparta_7dc1413727
@login_required(redirect_field_name='login')
def sparta_6d6e7a0a78(request):A=request;B=qube_316bac807a.sparta_a7855bf3fb(A);B['menuBar']=-1;C=qube_316bac807a.sparta_ec1a87b7f8(A.user);B.update(C);return render(A,'dist/project/homepage/homepage.html',B)