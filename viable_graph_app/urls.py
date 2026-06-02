from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path(
        "api/chart-data/", views.problem_chart_data, name="chart_data"
    ),  # ลิงก์สำหรับดึงสถิติไปทำกราฟ
    path("search/", views.search, name="search"),
    path("propose-solution/", views.propose_solution, name="propose_solution"),
    path("graph/", views.graph, name="graph"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("sign_up/", views.sign_up, name="sign_up"),
    path("about-us/", views.about_us, name="about_us"),
    path("define-problem/", views.define_problem, name="define_problem"),
    path("profile/", views.profile, name="profile"),
    path("propose_solutions/", views.propose_solutions, name="propose_solutions"),
    path("propose_solutions_2/", views.propose_solutions_2, name="propose_solutions_2"),
    path("reset_pass/", views.reset_pass, name="reset_password"),
    path("upload-photo/", views.upload_photo, name="upload_photo"),
     path("api/check-image-safety/", views.check_image_safety, name="check_image_safety"),
]
