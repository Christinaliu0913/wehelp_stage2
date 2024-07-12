// component 的 script 部分 
mounted(){
    TPDirect.setupSDK(APP_ID, APP_KEY, 'sandbox');
 
    const fields = {
      number: {
        element: this.$refs.number,
        placeholder: '**** **** **** ****',
      },
      expirationDate: {
        element: this.$refs.expirationDate,
        placeholder: 'MM/YY',
      },
      ccv: {
        element: this.$refs.ccv,
        placeholder: '後三碼',
      },
    };
 
    TPDirect.card.setup({
      fields: fields,
      styles: {
        // Style all elements
        input: {
          color: 'gray',
        },
        // Styling ccv field
        'input.cvc': {
          'font-size': '16px',
        },
        // Styling expiration-date field
        'input.expiration-date': {
          // 'font-size': '16px'
        },
        // Styling card-number field
        'input.card-number': {
          // 'font-size': '16px'
        },
        // style focus state
        ':focus': {
          // 'color': 'black'
        },
        // style valid state
        '.valid': {
          color: 'green',
        },
        // style invalid state
        '.invalid': {
          color: 'red',
        },
        // Media queries
        // Note that these apply to the iframe, not the root window.
        '@media screen and (max-width: 400px)': {
          input: {
            color: 'orange',
          },
        },
      },
    });
 
    TPDirect.card.onUpdate(update => {
      if (update.canGetPrime) {
        //全部欄位皆為正確 可以呼叫 getPrime
        this.disabledBtnPay = false;
      } else {
        this.disabledBtnPay = false;
      }
 
      this.updateStatus(update.status.number);
      this.updateStatus(update.status.expiry);
      this.updateStatus(update.status.number);
    });
  },
 
  methods: {
    updateStatus(field) {
      switch (field) {
        case 0:
          //欄位已填好，並且沒有問題
          console.log('field is ok');
          break;
        case 1:
          //欄位還沒有填寫
          console.log('field is empty');
          break;
        case 2:
          //欄位有錯誤，此時在 CardView 裡面會用顯示 errorColor
          console.log('field has error');
          break;
        case 3:
          //使用者正在輸入中
          console.log('usertyping');
          break;
        default:
          console.log('error!');
      }
    },
 
    // 觸發去取得狀態 
    onSubmit(){
      const tappayStatus = TPDirect.card.getTappayFieldsStatus();
      if (tappayStatus.canGetPrime === false) {
        // can not get prime
        return;
      }
 
      // Get prime
      TPDirect.card.getPrime(result => {
        if (result.status !== 0) {
          // get prime error
          console.log(result.msg);
          return;
        }
 
        let prime = result.card.prime;
 
        this.submitPrime(prime);
      });
    },
 
    async submitPrime(prime){
        try{
            // 要把得到的Prime Token 送給後端, 
            let payReslut = await apiPayByPrime(prime);
            if (payReslut.result.status === 0) {
            this.$notify({
                group: 'paidSuccess',
                type: 'success',
                text: '付款成功, （僅為展示頁面,不會進行出貨）',
            });
    
            this.createAnOrder();
            this.setStep(3);
            } else {
            this.$notify({
                group: 'paidFail',
                type: 'warn',
                text: '無法進行付款',
            });
            }
        } catch (err) {
            console.log(err);
        }
    }
    }