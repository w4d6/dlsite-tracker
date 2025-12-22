/**
 * DLsite Tracker - Google Apps Script
 * スプレッドシートの「拡張機能」→「Apps Script」に貼り付けて使用
 */

// 対象作品のID
const PRODUCT_IDS = [
  "RJ01486587",  // 予告ページ
  "RJ01470011",  // 作品ページ
];

/**
 * メイン実行関数 - 手動実行またはトリガーから呼び出し
 */
function fetchDLsiteData() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const today = Utilities.formatDate(new Date(), "Asia/Tokyo", "yyyy-MM-dd");

  // ヘッダーがなければ追加
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(["実行日付", "タイトル", "URL", "お気に入り数", "販売数"]);
  }

  PRODUCT_IDS.forEach(function(productId) {
    try {
      const data = fetchProductInfo(productId);
      if (data) {
        const isAnnounce = data.is_ana === true;
        const url = isAnnounce
          ? `https://www.dlsite.com/maniax/announce/=/product_id/${productId}.html`
          : `https://www.dlsite.com/maniax/work/=/product_id/${productId}.html`;

        const dlCount = data.dl_count !== null ? data.dl_count : "N/A";

        sheet.appendRow([
          today,
          data.work_name || "Unknown",
          url,
          data.wishlist_count || 0,
          dlCount
        ]);

        Logger.log(`Added: ${data.work_name}`);
      }
    } catch (error) {
      Logger.log(`Error fetching ${productId}: ${error}`);
    }
  });

  Logger.log("Done!");
}

/**
 * DLsite APIから作品情報を取得
 */
function fetchProductInfo(productId) {
  const apiUrl = `https://www.dlsite.com/maniax/product/info/ajax?product_id=${productId}`;

  const options = {
    method: "get",
    muteHttpExceptions: true,
    headers: {
      "Accept": "application/json",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
  };

  const response = UrlFetchApp.fetch(apiUrl, options);
  const responseCode = response.getResponseCode();

  if (responseCode !== 200) {
    Logger.log(`HTTP Error ${responseCode} for ${productId}`);
    return null;
  }

  const json = JSON.parse(response.getContentText());
  return json[productId] || null;
}

/**
 * テスト用 - 1件だけ取得してログに出力
 */
function testFetch() {
  const data = fetchProductInfo("RJ01470011");
  Logger.log(JSON.stringify(data, null, 2));
  Logger.log(`タイトル: ${data.work_name}`);
  Logger.log(`お気に入り: ${data.wishlist_count}`);
  Logger.log(`販売数: ${data.dl_count}`);
}

/**
 * 毎日のトリガーを設定
 */
function createDailyTrigger() {
  // 既存のトリガーを削除
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === "fetchDLsiteData") {
      ScriptApp.deleteTrigger(trigger);
    }
  });

  // 毎日午前9時に実行するトリガーを作成
  ScriptApp.newTrigger("fetchDLsiteData")
    .timeBased()
    .atHour(9)
    .everyDays(1)
    .inTimezone("Asia/Tokyo")
    .create();

  Logger.log("Daily trigger created for 9:00 AM JST");
}
