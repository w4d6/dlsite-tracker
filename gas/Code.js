/**
 * DLsite Tracker - Google Apps Script
 * GitHubのCSVを読み込んでスプレッドシートに追記
 */

const SPREADSHEET_ID = "1dxg6vN351JC6Zg2Set2ipq7Dp7H5lzbJRgdmyG7X30g";
const CSV_URL = "https://raw.githubusercontent.com/w4d6/dlsite-tracker/master/data/latest.csv";

/**
 * GitHubからCSVを取得してスプレッドシートに追記
 */
function fetchFromGitHub() {
  var spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = spreadsheet.getActiveSheet();

  // ヘッダーがなければ追加
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(["実行日付", "タイトル", "URL", "お気に入り数", "販売数", "取得元"]);
  }

  try {
    var response = UrlFetchApp.fetch(CSV_URL, { muteHttpExceptions: true });

    if (response.getResponseCode() !== 200) {
      Logger.log("HTTP Error: " + response.getResponseCode());
      return;
    }

    var csv = response.getContentText();
    var rows = Utilities.parseCsv(csv);

    Logger.log("CSV rows: " + rows.length);

    // ヘッダー行をスキップしてデータを追加
    for (var i = 1; i < rows.length; i++) {
      sheet.appendRow(rows[i]);
      Logger.log("Added: " + rows[i][1]);
    }

    Logger.log("Done! Added " + (rows.length - 1) + " records.");

  } catch (e) {
    Logger.log("Error: " + e.toString());
  }
}

/**
 * 毎日のトリガーを設定（GitHub Actionsの30分後）
 */
function createDailyTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    ScriptApp.deleteTrigger(triggers[i]);
  }

  // 毎日9:30 JST（GitHub Actionsの後）
  ScriptApp.newTrigger("fetchFromGitHub")
    .timeBased()
    .atHour(9)
    .nearMinute(30)
    .everyDays(1)
    .inTimezone("Asia/Tokyo")
    .create();

  Logger.log("Trigger created: 9:30 JST");
}

/**
 * GETリクエストでステータス確認
 */
function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    status: "ok",
    message: "DLsite Tracker API is running"
  })).setMimeType(ContentService.MimeType.JSON);
}
