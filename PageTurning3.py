import os
import shutil
from pdf2image import convert_from_path

# 取得目前程式碼所在的資料夾路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. 設定檔案路徑
original_pdf = os.path.join(BASE_DIR, "file", "doter 版面.pdf") 
temp_pdf = os.path.join(BASE_DIR, "temp_convert.pdf") 
output_folder = os.path.join(BASE_DIR, "flipbook_assets")
poppler_bin = r'C:\Mina\poppler-25.12.0\Library\bin'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

if not os.path.exists(original_pdf):
    print(f"❌ 找不到檔案：{original_pdf}")
else:
    print("🚀 檔案已找到，正在轉換 PDF 頁面為圖片...")
    shutil.copy(original_pdf, temp_pdf)

    image_paths = []
    try:
        pages = convert_from_path(temp_pdf, dpi=150, poppler_path=poppler_bin)
        
        for i, page in enumerate(pages):
            img_name = f"page_{i:03}.jpg".lower()
            img_path = os.path.join(output_folder, img_name)
            page.save(img_path, "JPEG")
            image_paths.append(img_name)
            print(f"✅ 已完成第 {i+1} 頁")
            
        # 3. 生成 HTML (分段組合，避免 f-string 混亂)
        # 注意：CSS 的 { } 在 f-string 中要寫成 {{ }}
        html_start = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>翻頁電子書</title>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/turn.js/3/turn.min.js"></script>
            <style>
                body {{ background: #1a1a1a; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
                #book {{ width: 1000px; height: 707px; box-shadow: 0 0 50px rgba(0,0,0,0.5); cursor: grab; }}
                #book:active {{ cursor: grabbing; }}
                .page {{ width: 500px; height: 707px; background-color: white; background-size: 100% 100%; background-repeat: no-repeat; background-position: center; border: 1px solid #333; }}
            </style>
        </head>
        <body>
        <div id="book">
        """

        html_pages = ""
        for img in image_paths:
            # 修正：確保變數名稱與上方一致，並使用 ./ 接路徑
            html_pages += f'            <div style="background-image:url(./flipbook_assets/{img})" class="page"></div>\n'
        
        html_end = """
        </div>
        <script>
            $(window).on('load', function() {
                if ($.isFunction($('#book').turn)) {
                    $('#book').turn({
                        width: 1000,
                        height: 707,
                        autoCenter: true,
                        gradients: true,
                        acceleration: true,
                        elevation: 100
                    });
                } else {
                    console.error("Turn.js 未能正確載入！");
                }
            });

            $("#book").bind("click", function(e) {
                var offset = $(this).offset();
                var relativeX = (e.pageX - offset.left);
                if (relativeX > 500) {
                    $('#book').turn('next');
                } else {
                    $('#book').turn('previous');
                }
            });

            $(window).bind('keydown', function(e) {
                if (e.keyCode == 37) $('#book').turn('previous');
                else if (e.keyCode == 39) $('#book').turn('next');
            });
        </script>
        </body>
        </html>
        """
        
        # 寫入檔案
        with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_start + html_pages + html_end)
        
        # 強制生成 .nojekyll (這對 GitHub Pages 很重要)
        with open(os.path.join(BASE_DIR, ".nojekyll"), "w") as f:
            f.write("")

        print("\n✨ 製作完成！請上傳 index.html, .nojekyll 和 flipbook_assets 資料夾到 GitHub。")

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)