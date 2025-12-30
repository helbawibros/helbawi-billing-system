function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = JSON.parse(e.postData.contents);
  
  // الترتيب حسب أعمدتك من A إلى I
  // A: الإجمالي | B: السعر | C: العدد | D: الصنف | E: اسم الزبون | F: رقم الزبون | G: رقم الفاتورة | H: المندوب | I: التاريخ
  
  var rowData = [
    data.total,      // A: الإجمالي
    data.price,      // B: السعر
    data.qty,        // C: العدد
    data.item,       // D: الصنف
    data.customer,   // E: اسم الزبون
    data.cust_no,    // F: رقم الزبون (اختياري حالياً)
    data.inv_no,     // G: رقم الفاتورة
    data.user,       // H: المندوب
    new Date()       // I: التاريخ
  ];
  
  sheet.appendRow(rowData);
  return ContentService.createTextOutput("Success");
}
