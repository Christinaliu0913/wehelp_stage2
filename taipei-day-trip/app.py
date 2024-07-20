from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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
import json
import httpx
import logging
from dotenv import load_dotenv, dotenv_values
import os 



app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #允許所有來源的請求
    allow_credentials=True, #允許跨域請求攜帶憑證(ex. cookeis) ，如果需要在跨區請求中使用憑證，需要設置為"TRUE"
    allow_methods=["*"], #允許所有HTTP方法(get,post,put....)
    allow_headers=["*"], #允許所有標頭(headers)
)

# KEY setting

load_dotenv('.env.develop')
## sql
db_database = os.getenv('DB_DATABASE')
db_password_local = os.getenv('DB_PASSWORD_LOCAL')
db_passowrd = os.getenv('DB_PASSWORD')

## tappay
merchantID = os.getenv('TAPPAY_MERCHANT_ID')
partnerKey = os.getenv('TAPPAY_PARTNER_KEY')

print(f'DB_DATABASE:',db_database)
print(f'DB_PASSWORD:',db_password_local)

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
	description: Optional[str]
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
### Booking 資料型態
class BookingPost(BaseModel):
	attractionId: int
	date: str
	time: str
	price: int
class BookingAttraction(BaseModel):
	attractionId: int
	name: str
	address: str
	image: str
class BookingResponse(BaseModel):
	attraction: Optional[List[BookingAttraction]]
	date: Optional[str]
	time: Optional[str]
	price: Optional[int]
### Order 資料型態
class Trip(BaseModel):
	attraction: BookingAttraction
	date: str
	time: str
class Contact(BaseModel):
	name: str
	email: str
	phone: str
class Order(BaseModel):
	price: int
	trip: Trip
	contact: Contact
class OrderForm(BaseModel):
	prime: str
	order: Order
class OrderCheckdata(BaseModel):
	number: str
	price: int
	trip: Trip 
	contact: Contact
	status: bool
#-----------------------連線至mysql-------------------------------|
db={
	"user":"root",
	"host":"localhost",
	"database":db_database,
	"password":db_passowrd
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
# @app.exception_handler(RequestValidationError)
# async def validation_exception(req: Request, exc: RequestValidationError):
# 	return RedirectResponse(url='/')

# @app.exception_handler(HTTPException)
# async def http_exception_handler(req: Request, exc: HTTPException):
# 	return JSONResponse(
# 		status_code= exc.status_code,
# 		content={'message': exc.detail},
	# )
### 處理其他異常
# @app.exception_handler(Exception)
# async def global_exception(req: Request, exc: Exception):
# 	return RedirectResponse(url='/')

#--------------------password------------------------------------|
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


	



## -------------------------------------API Order------------------------------------------
### TapPay setting
tapPayURL = 'https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

### 建立新的訂單，並完成付款程序
@app.post('/api/orders', response_class= JSONResponse)
async def post_order(res: Request,order: OrderForm):
	#登入驗證
	token = res.headers.get('Authorization')
	if not token:
		raise HTTPException(detail={"error":True,"message":"未登入系統"},status_code=403)
	token = token.split(' ')[1]
	
	try:
		payload = verify_token(token)
		user_id = payload['user_id']
		
		con = connect_sql()
		cursor = con.cursor()
		#創建訂單編號
		
		order_number = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
		#創建訂單
		cursor.execute(
			'''INSERT INTO booking(user_id,attractionID,date,time,price,booking_name,email,phone,order_number) 
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
			''',(user_id, order.order.trip.attraction.attractionId, order.order.trip.date, order.order.trip.time, order.order.price, order.order.contact.name, order.order.contact.email, order.order.contact.phone, order_number )
		)
		con.commit()

		if cursor.rowcount == 0:
			return JSONResponse(content={'error': True, 'message': '預定行程失敗，請重新遞交表單'}, status_code=400)
		
		#付款
		payByPrime = {
			'prime': order.prime,
			'partner_key': 'partner_XwOOWRbXKjjZZjmDtUNIcQvwDQwlcJ7tlyrF4bsK3sp2BeGU88KCeqec',
			'merchant_id': 'wehelptest_TAISHIN',
			'details': 'TapPay Test',
			'amount': order.order.price,
			'cardholder':{
				'phone_number': order.order.contact.phone,
				'name': order.order.contact.name,
				'email': order.order.contact.email,
			},
			'remember': True
		}
		headers={
				'Content-Type': 'application/json',
				'x-api-key': partnerKey
			}
		#跑tapPay交易
		

		async with httpx.AsyncClient() as client :
			response = await client.post(tapPayURL, headers=headers
			, json = payByPrime)
			#付款成功or失敗
			result =  response.json()
			
	
		#付款成功status=0(int)
		payment_status = result['status']
		if payment_status != 0:
			payment = {
				'status': payment_status,
				'message': result['msg']
			}
			return JSONResponse(content={'error': True, 'message': payment['message']}, status_code=400)
		else:
			payment = {
				'status': 0,
				'message': '付款成功'
			}
			#標記paymentstatus
			cursor.execute(
				'UPDATE booking SET payment_status = TRUE WHERE order_number = %s',(order_number, )
			)
			con.commit()
			#重置訂購
			cursor.execute(
			'''
			UPDATE member SET attractionID = NULL, date = NULL, time = NULL, price = NULL WHERE id =%s;
			''',(user_id, )
			)
			con.commit()

		data = {
			'number': order_number,
			'payment': payment
		}
		return JSONResponse(content={'data': data}, status_code= 200)
		
	except Exception as e:
		logger.error(f"Error processing payment: {e}")  
		return JSONResponse(content={"error": True, "message": f"{e}連線錯誤，請重新註冊"}, status_code=500)
	finally:
		cursor.close()
		con.close()

### 根據訂單編號取得訂單資訊
@app.get('/api/orders/{orderNumber}', response_class= JSONResponse)
def getOrder(res: Request, orderNumber: str):
	#登入驗證
	token = res.headers.get('Authorization')
	if not token:
		raise HTTPException(detail={"error":True,"message":"未登入系統"},status_code=403)
	token = token.split(' ')[1]
	
	try:
		payload = verify_token(token)
		user_id = payload['user_id']
		
		con = connect_sql()
		cursor = con.cursor()

		#獲取訂單資訊
		cursor.execute(
			'''
				SELECT order_number, price, attractionID, date, time, booking_name, email, phone, payment_status 
				FROM booking WHERE order_number = %s
			''',(orderNumber, )
		)

		orderInfor = cursor.fetchone()
		if not orderInfor:
			return JSONResponse(content={'error':True,'message':'未查找到此訂單'},status_code=400)
		

		attractionID = orderInfor[2]
		if attractionID:
			#獲取景點資訊
			cursor.execute(
				'SELECT name, address, images FROM attraction WHERE id = %s',(attractionID,)
			)
		attractionInfor = cursor.fetchone()
		image = attractionInfor[2].split('.')[0]

		data ={
			'number': orderInfor[0],
			'price': orderInfor[1],
			'trip': {
				'attraction':{
					'id': attractionID,
					'name': attractionInfor[0],
					'address': attractionInfor[1],
					'image': image
				},
				'date': orderInfor[3].strftime('%Y-%m-%d'),
				'time': orderInfor[4],
			},
			'contact': {
				'name': orderInfor[5],
				'email': orderInfor[6],
				'phone': orderInfor[7]
			},
			'status': orderInfor[8]
		}	
		print('傳送資料',data)
		return JSONResponse(content={'data': data}, status_code = 200)
		
	except mysql.connector.Error as e:
		print(f'Error:{e}')
		return JSONResponse(content={"error":True,'message':'連線錯誤，請重新嘗試'},status_code=500)
	finally:
		con.close()
		cursor.close() 



## --------------------------------------API Booking---------------------------------------
### 取得會員預定資訊
@app.get('/api/booking', response_class= JSONResponse)
def getBooking(res: Request):
	token = res.headers.get('Authorization')
	#若是沒有token代表沒有登入
	if not token:
		raise HTTPException(detail={"error":True,"message":"未登入系統"},status_code=403)
	token = token.split(' ')[1]
	
	try: 
		payload = verify_token(token)
		user_id = payload['user_id']
		
		con=connect_sql()
		cursor=con.cursor()

		cursor.execute(
			'select attractionID, date, time, price from member where id = %s;',(user_id,))
		booking = cursor.fetchone()

		if not booking or booking[0] is None:
			return JSONResponse(content={'data': None},status_code=200)
		
		attraction_id = booking[0]
		cursor.execute('SELECT id, name, address, images FROM attraction WHERE id = %s;',(attraction_id,))
		attraction = cursor.fetchone()

		if attraction : 
			attraction_image = attraction[3].split(',')[0] if attraction[3] else None
			data = {
				'data':{
					'attraction':{
						'id': int(attraction[0]),
						'name': attraction[1],
						'address': attraction[2],
						'image': attraction_image
					},
				'date': booking[1].strftime('%Y-%m-%d'),
				'time': booking[2],
				'price': int(booking[3])
				}
			}
			return JSONResponse(content=data,status_code=200)
		else:
			return JSONResponse(content={'data':None},status_code=200)
	except mysql.connector.Error as e:
		print(f'Error:{e}')
		return JSONResponse(content={"error":True,'message':'連線錯誤，請重新嘗試'},status_code=500)
	finally:
		con.close()
		cursor.close() 

### 預定行程
@app.post('/api/booking', response_class= JSONResponse)
def postBooking(res: Request,booking: BookingPost):
	token = res.headers.get('Authorization')
	if not token: 
		raise HTTPException(detail={'error':True,'message':'未登入系統'},status_code=403)
	
	token = token.split(' ')[1]

	try:
		payload = verify_token(token)
		user_id = payload['user_id']

		con=connect_sql()
		cursor=con.cursor()


		cursor.execute(
			'''
			SELECT attractionID, date, time FROM member WHERE id =%s;
			''',(user_id,)
		)
		result  = cursor.fetchone()
		if result:
			attractionid, date,time = result
			if attractionid == booking.attractionId and str(date) == booking.date and time == booking.time:
				return JSONResponse(content={'error': True, 'message': '已預定此行程'}, status_code=400)

		cursor.execute(
			'''
			UPDATE member SET attractionID = %s, date = %s, time = %s, price =%s WHERE id =%s;
			''',(booking.attractionId, booking.date, booking.time, booking.price,user_id)
		)
		con.commit()
		if cursor.rowcount > 0:
			return JSONResponse(content={'ok': True},status_code=200)
		else:
			return JSONResponse(content={'error': True, 'message': '預定行程失敗'}, status_code=400)
	except mysql.connector.Error:
		return JSONResponse(content={"error":True,'message':'連線錯誤，請重新嘗試'},status_code=500)
	finally:
		cursor.close()
		con.close()
		 

## 刪除行程
@app.delete('/api/booking', response_class= JSONResponse)
def deleteBooking(res: Request):
	token = res.headers.get('Authorization')
	if not token: 
		raise HTTPException(content={'error':True,'message':'未登入系統'},status_code=403)
	token = token.split(' ')[1]
	
	try: 
		payload = verify_token(token)
		user_id = payload['user_id']
		con=connect_sql()
		cursor = con.cursor()

		cursor.execute(
			'''
			UPDATE member SET attractionID = NULL, date = NULL, time = NULL, price = NULL WHERE id =%s;
			''',(user_id, )
		)
		con.commit()
		
		if cursor.rowcount > 0:
			return JSONResponse(content={'ok':True},status_code=200)
	except mysql.connector.Error:
		return JSONResponse(content={"error":True,'message':'連線錯誤，請重新嘗試'},status_code=500)
	finally:
		con.close()
		cursor.close() 


## -------------------------------------API User---------------------------------------
### 登入會員帳戶 (PUT)
@app.put("/api/user/auth", response_class = JSONResponse)
def sign_in(user: UserResponse):
	con=connect_sql()
	cursor=con.cursor()
	try:
		cursor.execute('SELECT id, name, password FROM member where email=%s ',(user.email, ))
		result = cursor.fetchone()

		
		#登入失敗，密碼帳號錯誤
		if result is None :
			return JSONResponse(content={"error":True,'message':'無此帳號'},status_code=400)
		#獲得使用者id、使用者名稱、加密密碼
		user_id, name, hashed_password = result

		if not verify_password(user.password,hashed_password):
			return JSONResponse(content={"error":True,'message':'密碼錯誤'},status_code=400)
		
		#生成JWT token
		token = create_access_token(data={'user_id': user_id, 'name': name, 'email':user.email})
		return JSONResponse(content={'token':token})
	except mysql.connector.Error:
		return JSONResponse(content={"error":True,'message':'連線錯誤，請重新嘗試'},status_code=500)
	finally:
		cursor.close()
		con.close()


### 取得當前登入的會員資訊 (GET)
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


## -------------------------------------API Attractions 取得景點資料表-----------------------------------------------
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
# if __name__=='__main__':
# 	import uvicorn
# 	uvicorn.run(app, host='127.0.0.1', port=8000)
