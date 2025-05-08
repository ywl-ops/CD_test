'''
Author: '夜微凉'
Date: 2025-05-08 10:48:36
LastEditors: '夜微凉'
LastEditTime: 2025-05-08 10:48:50
FilePath: /CD_test/test.py
Description: 

'''
echo "# CD_test" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/ywl-ops/CD_test.git
git push -u origin main