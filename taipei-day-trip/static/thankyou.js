//-------------------load---------------------------|
const token = localStorage.getItem('token')
const getTokenURL = '/api/user/auth' 
window.addEventListener('load',function(){
    checkSigned();
    //獲取景點id訊息
    const orderNumber = getOrderNumber();

    if(orderNumber){
        console.log(`orderNumber: ${orderNumber}`);
        getOrderAPI(orderNumber);
    }else{
        alert('查無此訂單')
        console.log('not valid orderNumber')
        window.location.href = '/'
    }
    
});

function getOrderNumber(){
    const orderNumber = new URLSearchParams(window.location.search);
    return orderNumber.get('orderNumber');
}

//get orders API
function getOrderAPI(orderNumber){
    fetch(`api/orders/${orderNumber}`,{
        method:'GET',
        headers:{
            'Authorization':`Bearer ${token}`,
            'Content-Type':'application/json'
        }
    }).then(res => res.json())
    .then(result =>{
        console.log(result)
        renderPage(result); 
        
    })
    .catch(error => {
        alert(error.meessage);
    })
}

//訂購畫面
function renderPage(data){
    const orderNumber = data.data.number;
    const orderName = data.data.contact.name;
    if(data.data.status = 1){
        document.querySelector('#paymentStatus').textContent = '訂購成功！';
        document.querySelector('#img').src='/static/img/accept.png';
        document.querySelector('#orderName').textContent = orderName;
        document.querySelector('#orderNumber').textContent = orderNumber; 
    }else if(data.data.status = 0){
        document.querySelector('#img').src='/static/img/warning.png';
        document.querySelector('#paymentStatus').textContent = '付款失敗！'
        document.querySelector('#orderName').textContent = orderName;
        document.querySelector('#orderNumber').textContent = orderNumber; 
        //設置回到上一頁
        const repayButtonDiv = document.querySelector('#ifUnpaid')
        const repayButton = document.createElement('button');
        repayButton.classList.add('repay');
        repayButton.textContent = '重新付款'
        repayButtonDiv.appendChild(repayButton);
    }
    

}

//檢查是否登入狀態
async function checkSigned(){
    if (!token){
      window.location.href='/'
      return;//直接返回
    }

    try{
      const tokenRes = await fetch(getTokenURL,{
        method: 'GET',
        headers:{
          'Authorization' : `Bearer ${token}` //發送token進行驗證
        }
      })
      if(tokenRes.ok){
        const tokenResult = await tokenRes.json();
        Showsigned();
        console.log("Login verified:", tokenResult);
        localStorage.setItem('user_data', JSON.stringify(tokenResult.data))
      }else{
        console.error('Failed to verify login', await tokenRes.json());
        localStorage.removeItem('token');//驗證失敗，清除不正確的token
      }
    }catch(error){
        console.error('Error:',error);
        alert('加油好嗎？');
      }
    
  };
//登入後navigationbar變動
  function Showsigned(){
    document.getElementById('nav-signin').style.display = 'none';
    document.getElementById('nav-signout').style.display = 'flex';
  }
  function signOut(){
    localStorage.removeItem('token');
    alert('成功登出！');
    window.location.href='/';
  }