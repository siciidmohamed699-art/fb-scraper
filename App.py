from flask import Flask, request, send_file, render_template_string
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
import io

app = Flask(__name__)

@app.route("/fb", methods=["GET", "POST"])
def scrape_fb():
    if request.method == "POST":
        page_url = request.form["url"]
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        wb = Workbook()
        ws = wb.active
        ws.title = "Facebook Posts"
        ws.append(["Date", "Post Text", "Link"])

        posts = soup.find_all("div", {"role": "article"})
        for post in posts:
            text_div = post.find("div", {"dir": "auto"})
            text = text_div.get_text(strip=True) if text_div else "N/A"
            time_tag = post.find("a", {"aria-hidden": "true"})
            date = time_tag.get_text(strip=True) if time_tag else "N/A"
            link = "https://facebook.com" + time_tag["href"] if time_tag and "href" in time_tag.attrs else "N/A"
            ws.append([date, text, link])

        file_stream = io.BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)
        return send_file(file_stream, as_attachment=True, download_name="fb_posts.xlsx")

    return render_template_string("""
        <h2>Facebook Page Scraper</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="Enter Facebook Page URL" style="width:300px;" required>
            <button type="submit">Download Excel</button>
        </form>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
