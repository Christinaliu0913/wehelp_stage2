from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from typing import List, Optional
from pydantic import BaseModel
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

import jwt
from jwt import PyJWTError
from jwt.exceptions import InvalidTokenError,ExpiredSignatureError
import datetime
import secrets
from passlib.context import CryptContext


app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #允許所有來源的請求
    allow_credentials=True, #允許跨域請求攜帶憑證(ex. cookeis) ，如果需要在跨區請求中使用憑證，需要設置為"TRUE"
    allow_methods=["*"], #允許所有HTTP方法(get,post,put....)
    allow_headers=["*"], #允許所有標頭(headers)
)
#---------------------BaseModel資料型態----------------------|
### User 資料型態
class User(BaseModel):
	name: str
	email: str
	password: str
class UserResponse(BaseModel):
	email: str
	password: str
### Attraction的資料型態
class Attraction(BaseModel):
	id: int
	name: str
	category: Optional[str]
	description: str
	address: Optional[str]
	transport: Optional[str]
	mrt: Optional[str]
	lat: float
	lng: float
	images: List[str]
class AttractionResponse(BaseModel):
	nextpage:Optional[int]
	data: List[Attraction]
class AttractionIDResponse(BaseModel):
	data: List[Attraction]
class MrtStationResponse(BaseModel):
	data: List
#-----------------------連線至mysql-------------------------|
db={
	"user":"root",
	"host":"localhost",
	"database":"taipei",
	"password":"12345678"
}
def connect_sql():
	con = mysql.connector.connect(**db)
	return con

# --------Static Pages (Never Modify Code in this Block)-------|
# 可加不可動！
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")

# -------------------處理錯誤->導回首頁---------------------------|

### 當請求驗證錯誤的時候 
@app.exception_handler(RequestValidationError)
async def validation_exception(req: Request, exc: RequestValidationError):
	return RedirectResponse(url='/')
### 處理其他異常
@app.exception_handler(Exception)
async def global_exception(req: Request, exc: Exception):
	return RedirectResponse(url='/')

#----------------password---------------------|
#創建cryptContext對象->使用bcrypt演算法/
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')#deprecated自動處理過期的哈希算法

def verify_password(plain_password, hashed_password):
	return pwd_context.verify(plain_password,hashed_password)

def get_password_hash(password):
	return pwd_context.hash(password)

# -------------------JWT Token----------------------------------|
#JWT 配置
secret_key = secrets.token_urlsafe(32)#生成一個隨機的密鑰
alg = 'HS256'
access_token_expire_days = 7 

#生成JWT Token
#data={'user_id': user_id, 'name': name, 'email':user.email}
def create_access_token(data:dict, expires_delta: Optional[datetime.timedelta]=None):
	#確保不會直接修改原始的data字典，只在副本to_encode上進行修改
	to_encode = data.copy() 
	#設置過期時間
	if expires_delta:
		expire = datetime.datetime.utcnow() + expires_delta
	else:
		expire = datetime.datetime.utcnow() + datetime.timedelta(days = access_token_expire_days)
	#將expire更新至to_encode的字典中->Jwt標準中過期時間exp
	to_encode.update({'exp' : expire})
	#將to_encode字典編碼成一個JWT
	encoded_jwt = jwt.encode(to_encode, secret_key, algorithm = alg)
	return encoded_jwt


#驗證JWT Token

def verify_token(token:str):
	#錯誤時的狀態設定
	credentails_exception = HTTPException(
		status_code= 401,
		#錯誤訊息
		detail = 'Could not validate credentials',
		#HTTP頭訊息-> 需要Bearer Token進行身份驗證
		headers = {'WWWW-Authenticate' : 'Bearer'},
	)
	#解碼JWT
	try: 
		payload = jwt.decode(token, secret_key, algorithms = [alg])
		return payload
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e)) #伺服器處理請求時發生錯誤
	except InvalidTokenError:
		raise credentails_exception
	except ExpiredSignatureError:
		raise HTTPException(status_code=401, detail='token has expired')



## API User---------------------------------------
### 登入會員帳戶 (PUT)
@app.put("/api/user/auth", response_class=JSONResponse)
def sign_in(user: UserResponse):
	con=connect_sql()
	cursor=con.cursor()
	try:
		cursor.execute('SELECT id, name, password FROM member where email=%s and password=%s',(user.email, user.password))
		result = cursor.fetchone()
		#登入失敗，密碼帳號錯誤
		if result is None:
			return JSONResponse(content={"error":True,'message':'帳號或密碼錯誤'},status_code=400)
		user_id, name, password = result
		#生成JWT token
		token = create_access_token(data={'user_id': user_id, 'name': name, 'email':user.email})
		return JSONResponse(content={'token':token})
	except mysql.connector.Error:
		return JSONResponse(content={"error":True,'message':'連線錯誤，請重新嘗試'},status_code=500)
	finally:
		con.close()
		cursor.close()
		
#取得當前登入的會員資訊 (GET)
@app.get('/api/user/auth', response_class=JSONResponse)
def get_user_access(req: Request):
	token = req.headers.get('Authorization')
	#authorization header -> Bearer my_token
	if token is None:
		raise HTTPException(
			status_code = 401,
			detail = "Authorization header missing"
		)
	token = token.split(' ')[1] #get my_token(去掉Bearer)
	try:
		payload = verify_token(token)
		return JSONResponse(content={'data': payload}, status_code=200)
	except HTTPException as e:
		raise e
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
	
	

### 註冊會員
@app.post("/api/user",response_class=JSONResponse)
def sign_up(user: User):
	
	if '@' not in user.email:
		return JSONResponse(content={"error":True,"message":"電子郵件格式錯誤"},status_code=400)
	con=connect_sql()
	cursor=con.cursor()
	try:
		#檢查重複的Email 
		cursor.execute('SELECT COUNT(*) FROM member WHERE email = %s',(user.email,))
		result= cursor.fetchone()
		if result[0] > 0:
			return JSONResponse(content={"error":True, "message": "此電子信箱已被註冊"},status_code=400)
		#註冊新的使用者帳號
		hashed_password = get_password_hash(user.password)
		cursor.execute(
			'''
				INSERT INTO member(name,email,password) VALUES(%s,%s,%s)
			''',(user.name, user.email, hashed_password)
		)
		con.commit()
		return JSONResponse(content={"ok":True}, status_code=200)
	except mysql.connector.Error:
		return JSONResponse(content={"error":True,"message":"連線錯誤，請重新註冊"},status_code=500)
	finally:
		cursor.close()
		con.close()
		




## API Attractions 取得景點資料表-----------------------------------------------
@app.get("/api/attractions",response_model=AttractionResponse)
async def get_attraction(page:int= Query(0, alias="page"), keyword:str=Query("",alias="keyword")):
	#keyword用來完全比對捷運站名稱、或模糊比對景點名稱的關鍵字，沒有給定則不做篩選
	try: 
		per_pageInfo=12 #每頁12筆資料
		offset = max(0, (page) * per_pageInfo) #mysql限制offset從第幾筆資料開始
		con=connect_sql()
		cursor=con.cursor(dictionary=True)#結果以字典形式返回

		#若是有輸入關鍵字的話 data
		if keyword:
			#transport 是direction
			query='''SELECT id, name, category, description, address, 
				transport, mrt, lat, lng, images FROM
				attraction WHERE name LIKE %s OR mrt LIKE %s
				LIMIT %s OFFSET %s 
				'''
			cursor.execute(query,(f'%{keyword}%',f'%{keyword}%',per_pageInfo,offset))
		else:
			query='''
				SELECT id, name, category, description, address, 
				transport, mrt, lat, lng, images FROM
				attraction LIMIT %s OFFSET %s
				'''
			cursor.execute(query,(per_pageInfo,offset))
		attractions= cursor.fetchall()
		#圖片部分格式化為List
		for attraction in attractions:
			if attraction["images"]:
				attraction["images"]= attraction['images'].split(',')
		#獲取總數據條目來計算下一頁 next page
		if keyword:
			cursor.execute(
				'''
				SELECT COUNT(*) As count FROM attraction WHERE name LIKE %s 
				''',(f'%{keyword}%',)
			)
		else:
			cursor.execute(
				'''
				SELECT COUNT(*) AS count FROM attraction
				'''
			)
		results= cursor.fetchone()['count']	
		#如果所有的項目不超過58項則顯示下一頁
		next_page= page+1 if offset+per_pageInfo < results else None
		response= {
			"nextPage":next_page,
			"data":attractions
		}
		return JSONResponse(response,status_code=200)
	except mysql.connector.Error: 
		return JSONResponse(content={"error":True,'message':'伺服器內部錯誤'},status_code=500)
	finally:
		cursor.close()
		con.close()

### 取得景點編號取得景點資料
@app.get("/api/attraction/{attractionID}", response_model=AttractionIDResponse)
async  def get_attractionID(attractionID:int):
	try: 
		con=connect_sql()
		cursor=con.cursor(dictionary=True)
		cursor.execute(
			'''
			SELECT id, name, category, description, address, 
				transport, mrt, lat, lng, images FROM
				attraction WHERE id = %s
			''',(attractionID,)
		)
		attraction=cursor.fetchone()
		#錯誤訊息，請求無法正常處理的時候
		if not attraction:
			return JSONResponse(content={"error":True,"message":"景點編號不正確"},status_code=400)
		
		if attraction['images']:
			attraction['images']= attraction['images'].split(",")
		return JSONResponse(content={"data":attraction},status_code=200)
	except mysql.connector.Error:
		return JSONResponse(content={"error":True,'message':'伺服器內部錯誤'},status_code=500)
	finally: 
		cursor.close()
		con.close()


### 取得所有捷運站名稱列表，按照周邊景點的數量由大到小排序
@app.get("/api/mrts", response_model=MrtStationResponse)
async def mrt_station():
	try:
		con=connect_sql()
		cursor=con.cursor(dictionary=True)
		cursor.execute(
			'''
			SELECT mrt, COUNT(*) as count FROM attraction 
			WHERE mrt IS NOT NULL AND mrt !=''
			GROUP BY mrt 
			ORDER BY count DESC
			'''
		)
		mrt_result =[row['mrt'] for row in cursor.fetchall()]
		if mrt_result: 
			return JSONResponse(content={"data":mrt_result},status_code=200)
	except mysql.connector.Error:
		return JSONResponse(content={"error":True, "message":"伺服器內部錯誤"})
	finally:
		con.close()
		cursor.close()

	

if __name__=='__main__':
	import uvicorn
	uvicorn.run(app, host='0.0.0.0', port=8000)