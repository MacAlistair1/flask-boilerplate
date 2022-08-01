# Installation Process

- clone project

  - `git clone https://github.com/MacAlistair1/flask-boilerplate.git`

- Command after clone success

  - `python3 -m venv env` **virtual env**
  - `source env/bin/activate` **activate virtual env if required**
  - `pip install -r requirements.txt` **install requirements dependency modules**
  - `flask run` **serve the project**

- User & Auth Api EndPoint

  - `{BASE_URI}/api/v1/auth/register` `POST` **Register User**
  - `{BASE_URI}/api/v1/auth/verify-otp` `POST` **verify otp**
  - `{BASE_URI}/api/v1/auth/login` `POST` **User Login**
  - `{BASE_URI}/api/v1/auth/my-profile` `GET` **Auth Route For User Profile**
  - `{BASE_URI}/api/v1/auth/token/refresh` `GET` **Refresh accessToken using RefreshToken**

- Bookmark Api EndPoint
  - `{BASE_URI}/api/v1/bookmark` `GET` **Bookmark List**
  - `{BASE_URI}/api/v1/bookmark` `POST` **Store Bookmark**

- Swagger Api Docs

  - `{BASE_URI}/apidocs` **_Api document using Swagger_**
  - `{BASE_URI}//apispec.json` **_Swagger json file_**

<p align="center">
                   
<a href="mailto:info@jeevenlamichhane.com.np" target="_blank" title="Mail me ">
  
  <img src="https://user-images.githubusercontent.com/57852378/93742512-d8c74800-fc0b-11ea-9e64-ec554be7cd59.png"  width="40" height="40"/>
  
  </a>

   <a href="https://github.com/MacAlistair1" target="_blank" title="Explore Mac's code on github">
  
  <img src="https://user-images.githubusercontent.com/57852378/93742503-d664ee00-fc0b-11ea-8f75-db2448ff01f1.png"  width="40" height="40"/>
</a>
  <a href="https://jeevenlamichhane.com.np/" target="_blank" title="Visit My Website">

  <img src="https://user-images.githubusercontent.com/57852378/93742509-d7961b00-fc0b-11ea-958f-ed7497f3b785.png"  width="40" height="40"/>
  </a>

  <a href="https://np.linkedin.com/in/jeeven-lamichhane-%E2%9A%A1%F0%9F%8C%B9-36647816b" target="_blank" title="View My Profile on linkedin">
  <img src="https://user-images.githubusercontent.com/57852378/93742508-d7961b00-fc0b-11ea-9ed8-7ad7b25b71d8.png"  width="40" height="40"/>
  </a>

</p>
