from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Count
from .models import Problem


# 1. หน้าแรกปกติ (เรนเดอร์หน้า home.html)
def home_view(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "ROADS")
        description = request.POST.get("description", "").strip()

        if title and description:
            Problem.objects.create(
                title=title, category=category, description=description
            )
            messages.success(request, "ส่งรายงานปัญหาเรียบร้อยแล้ว")
            return redirect("home")
        else:
            messages.error(request, "กรุณากรอกหัวข้อและรายละเอียดให้ครบถ้วน")

    total_problems = Problem.objects.count()
    progress_problems = Problem.objects.filter(status="PROGRESS").count()
    completed_problems = Problem.objects.filter(status="COMPLETED").count()
    recent_problems = Problem.objects.all().order_by("-created_at")[:5]

    context = {
        "recent_problems": recent_problems,
        "total_problems": total_problems,
        "progress_problems": progress_problems,
        "completed_problems": completed_problems,
    }
    return render(request, "home.html", context)


# 2. API จ่ายข้อมูลดิบไปพล็อตกราฟ (ส่งข้อมูลเป็น JSON)
def problem_chart_data(request):
    # ไปนับจำนวนปัญหาแยกตามหมวดหมู่ในฐานข้อมูล
    data_query = Problem.objects.values("category").annotate(total=Count("id"))

    # จัดโครงสร้างข้อมูลให้อ่านง่ายสำหรับ Frontend
    labels = []
    values = []

    # แปลงชื่อย่อฐานข้อมูลเป็นภาษาไทยก่อนส่งออกไป
    category_map = dict(Problem.CATEGORY_CHOICES)

    for item in data_query:
        labels.append(category_map.get(item["category"], item["category"]))
        values.append(item["total"])

    return JsonResponse({"labels": labels, "data": values})


def search(request):
    q = request.GET.get("q", "")
    results = Problem.objects.filter(title__icontains=q)
    return render(request, "search.html", {"results": results, "query": q})


def propose_solution(request):
    return render(request, "propose_solutions.html")


def graph(request):
    return render(request, "graph.html")


def login(request):
    return render(request, "login.html")


def logout(request):
    return redirect("home")


def sign_up(request):
    return render(request, "sign_up.html")


def about_us(request):
    return render(request, "about_us.html")


def define_problem(request):
    return render(request, "define_problem.html")


def profile(request):
    return render(request, "profile.html")


def propose_solutions(request):
    return render(request, "propose_solutions.html")


def propose_solutions_2(request):
    return render(request, "propose_solutions_2.html")


def reset_pass(request):
    return render(request, "reset_pass.html")
