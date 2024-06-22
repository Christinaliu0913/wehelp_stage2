//|------------------登入/註冊-----------------------|

 //左右滑動
 function moveLeft(){
    document.getElementById('mrts-list').scrollLeft -= 450;
  }
  function moveRight(){
    document.getElementById('mrts-list').scrollLeft += 450;
  }
  //登入頁面
  function signIn(){
    document.querySelector('#signin').style.display = 'flex';
    document.querySelector('.overlay').style.display = 'flex';
    document.querySelector('#signup').style.display = 'none';
  }
  //返回
  function signinClose(){
    document.querySelector('#signin').style.display = 'none';
    document.querySelector('.overlay').style.display = 'none';
  }
  //註冊頁面
  function signUp(){
    document.querySelector('#signin').style.display = 'none';
    document.querySelector('#signup').style.display = 'flex';
    document.querySelector('.overlay').style.display = 'flex';
  }
  function signupClose(){
    document.querySelector('#signup').style.display = 'none';
    document.querySelector('.overlay').style.display = 'none';
  }



//---------attraction單頁page------------------|


//---------費用切換更新--------

function ChooseFee(){
    const feeElement = document.querySelector('#fee');
    const morningCheck = document.querySelector('#morning');
    const afternoonCheck = document.querySelector('#afternoon');

    if(morningCheck.checked){
        feeElement.textContent = '新台幣2000元';
    }else if(afternoonCheck.checked){
        feeElement.textContent = '新台幣2500元';
    }else{
        feeElement.textContent = '新台幣2000元';
    }
}
//---------景點資料的獲取-----

//將ID傳  入函數
window.addEventListener('load',function(){
    const attractionId = getAttractionIdFromURL();

    if(attractionId){
        console.log(`Attraction ID1: ${attractionId}`);
        AttractionIdAPI(attractionId);
    }else{
        console.log('not valid attractionID')
        window.location.href = '/'
    }
    
});

//獲取URL中景點ID
function getAttractionIdFromURL(){
    const attractionURLId = window.location.pathname.split('/');
    return attractionURLId[attractionURLId.length - 1];
}
//取得attractionId的內容
// function AttractionIdAPI(Id){
//     const attractionURL =`/api/attraction/${Id}`
//     console.log(`Attraction ID: ${attractionURL}`)
//     fetch(attractionURL).then(res =>{
//         if(res.status === 400 || res.status === 422 || res.status === 400){
//             res.json().then(result  => {
//                 console.error(result.message);
//                 window.location.href = '/';
//             });
//         }else{
//             return res.json().then(result =>{
//                 attractionIdData(result);
//             });
//         }
//         }).catch(error=>{
//             window.location.href = '/';
//             console.log("fail to fetch attractionID:",error);
//         });
// }
function AttractionIdAPI(Id){
    const attractionURL =`/api/attraction/${Id}`
    console.log(`Attraction ID: ${attractionURL}`)
    fetch(attractionURL).then(res =>{
            return res.json()
        }).then(result =>{
            attractionIdData(result);
        }).catch(error=>{
            window.location.href = '/';
            console.log("fail to fetch attractionID:",error);
        });
}

function attractionIdData(data){
const attractionData = data.data;
const attractionId = attractionData.id;
const attractionName = attractionData.name;
const attractionCat = attractionData.category;
const attractionMrt = attractionData.mrt;
const attractionDes = attractionData.description;
const attractionAddress = attractionData.address;
const attractionImg = attractionData.images;
const attractionTransport = attractionData.transport;
attractionInfo(attractionName,attractionCat,attractionMrt);
attractionIMG(attractionImg);
attractionDetail(attractionDes,attractionAddress,attractionTransport)
}

function attractionInfo(name,cat,mrt){
//上方景點名稱、種類、捷運站
const attractionInfoDiv = document.querySelector('.attraction-intro-info-upper');

const attractionInfoName = document.createElement('h3');
attractionInfoName.classList.add('attraction-intro-info-title');
attractionInfoName.textContent = name;

const attractionInfoCatMrt = document.createElement('div');
attractionInfoCatMrt.classList.add('attraction-intro-info-content');
attractionInfoCatMrt.textContent = `${cat} at ${mrt}`;

attractionInfoDiv.appendChild(attractionInfoName);
attractionInfoDiv.appendChild(attractionInfoCatMrt);
}
//下方說明欄
function attractionDetail(description,address,transportation){
const attractionDetailDesDiv = document.querySelector('.description');
const attractionDetailAddressDiv = document.querySelector('.address');
const attractionDetailTransDiv = document.querySelector('.transpor');

const attractionDetailDes = document.createElement('p');
attractionDetailDes.textContent = description;

const attractionDetailAddress = document.createElement('p');
attractionDetailAddress.textContent = address;

const attractionDetailtransport = document.createElement('p');
attractionDetailtransport.textContent = transportation;

attractionDetailDesDiv.appendChild(attractionDetailDes);
attractionDetailAddressDiv.appendChild(attractionDetailAddress);
attractionDetailTransDiv.appendChild(attractionDetailtransport);
}

//---------圖片輪播功能-------------------------|

function attractionIMG(imgs){
    const attractionIMGContainerDiv = document.querySelector('.attraction-intro-img-container');
    const attractionIMGIndicatorsDiv = document.querySelector('.attraction-intro-img-indicators');

    imgs.forEach((img,index)=>{
        //設置照片
        const carouselIMG = document.createElement('div')
        carouselIMG.classList.add('attraction-intro-img-carouselIMG');
        carouselIMG.style.backgroundImage = `url(${img})`
        if(index === 0){
            carouselIMG.classList.add('active');//讓第一張照片active
        }

        attractionIMGContainerDiv.appendChild(carouselIMG);

        //加入下方球球
        const carouselIndicator = document.createElement('div');
        carouselIndicator.classList.add('attraction-intro-img-indicator');
        if(index === 0){
            carouselIndicator.classList.add('active');
        }

        carouselIndicator.setAttribute('indicator-index',index)//設定每個球球的編號
        carouselIndicator.addEventListener('click', () => changeIMGbyIndicator(index));

        attractionIMGIndicatorsDiv.appendChild(carouselIndicator);
    })  
}

let currentIMGIndex = 0;//將index預設為第一張

function showIMG(index){
    const carouselIMGs = document.querySelectorAll('.attraction-intro-img-carouselIMG');
    const carouselIndicators = document.querySelectorAll('.attraction-intro-img-indicator');
    if (index >= carouselIMGs.length){//實現輪播的功能-> 超過照片組數時，循環到第一張照片
        currentIMGIndex = 0
    }else if(index < 0){//再看看
        currentIMGIndex = carouselIMGs.length -1;
    }else{
        currentIMGIndex = index;
    }

    carouselIMGs.forEach((img,index) =>{
        img.classList.toggle('active', index === currentIMGIndex);
    })
    carouselIndicators.forEach((indicator,index) =>{
        indicator.classList.toggle('active', index === currentIMGIndex)
    })
};

//用球球換照片
function changeIMGbyIndicator(index){
    showIMG(index)
}

//向左右滑一張照片
function imgLeft(){
    showIMG(currentIMGIndex - 1);
};
function imgRight(){
    showIMG(currentIMGIndex + 1);
};
