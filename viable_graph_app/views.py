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
            Problem.objects.create(title=title, category=category, description=description)
            return redirect("home")

    # ดึงข้อมูลปัญล่าสุด 5 อันดับแรกไปโชว์ที่หน้าเว็บด้วย
    recent_problems = Problem.objects.all().order_by("-created_at")[:5]
    context = {"recent_problems": recent_problems}
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
