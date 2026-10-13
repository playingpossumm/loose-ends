/**
 * Telegram relay: the bot's webhook, so nothing waits for a scheduled drain.
 *
 * Telegram pushes each update here the moment it is sent. A tap on the to-do checklist is
 * answered and ticked in the message at once; every update is then passed to the vault's
 * GitHub workflow (.github/workflows/telegram.yml), which saves the message or closes the
 * loop with scripts/telegram_capture.py --update, a minute or so later.
 *
 * The message is redrawn here with the same rules as render() in
 * scripts/telegram_checklist.py, so the workflow, which only redraws when the vault
 * disagrees, normally has nothing to change. Keep the two in step.
 *
 * Script properties, under Project Settings > Script properties:
 *   TELEGRAM_TOKEN   the bot token: BRAIN_TELEGRAM_TOKEN in .env
 *   CHAT_ID          your chat: BRAIN_TELEGRAM_CHAT_ID in .env
 *   GITHUB_TOKEN     a fine-grained token, Contents: read and write, on the vault repository only
 *   GITHUB_REPO      the vault repository, as owner/name
 *   WEB_APP_URL      this script's web app URL, from Deploy > Manage deployments
 * setUpWebhook() adds WEBHOOK_KEY itself.
 *
 * Setup: deploy as a web app (execute as you, access: anyone), add the properties, then run
 * setUpWebhook once from the editor. removeWebhook() goes back to draining.
 */

var props = PropertiesService.getScriptProperties();

var FOOTER = "Tap a number once it's done, and again to undo.";
var PER_ROW = 6;
var LINE = /^([☐☑✕]) (\d+)  (.+) · (.+)$/;

/** Telegram calls this. Returning nothing answers 200, which is what Telegram needs. */
function doPost(e) {
  // The key in the URL is the only thing that tells Telegram apart from anyone who finds it.
  if (!e || !e.parameter || e.parameter.key !== props.getProperty('WEBHOOK_KEY')) return;
  var update = JSON.parse(e.postData.contents);

  // Telegram resends an update it thinks went undelivered. Each is applied once.
  var cache = CacheService.getScriptCache();
  var seen = 'u' + update.update_id;
  if (cache.get(seen)) return;
  cache.put(seen, '1', 21600);

  var chat = String(props.getProperty('CHAT_ID'));
  var cq = update.callback_query;
  if (cq) {
    if (String(cq.from.id) !== chat || !cq.message || String(cq.message.chat.id) !== chat) return;
    // The tick on screen is a courtesy. Nothing here may stop the update reaching the vault.
    try {
      telegram('answerCallbackQuery', {callback_query_id: cq.id});
      tickNow(cq);
    } catch (err) {
      console.error('Could not tick the message: ' + err);
    }
  } else {
    var msg = update.message || update.channel_post;
    if (!msg || String(msg.chat.id) !== chat) return;
  }
  flushBacklog();
  var sent = false;
  try {
    sent = dispatch(update);
  } catch (err) {
    console.error('Could not reach GitHub: ' + err);
  }
  if (!sent) props.setProperty('pending_' + update.update_id, JSON.stringify(update));
}

/** Tick or untick the tapped line now, from the message as Telegram sent it with the tap. */
function tickNow(cq) {
  var data = String(cq.data || '');
  var action = data.split(':')[0];
  var key = data.slice(action.length + 1);
  if ((action !== 'd' && action !== 'u') || !key) return;

  var msg = cq.message;
  var lines = String(msg.text || '').split('\n');
  var listed = {};
  lines.forEach(function (l) {
    var m = LINE.exec(l);
    if (m) listed[m[2]] = {title: m[3], when: m[4]};
  });
  // A checklist from before the list moved into the message: the workflow relabels it.
  if (!Object.keys(listed).length) return;

  var buttons = [].concat.apply([], (msg.reply_markup || {}).inline_keyboard || []);
  var rows = [];
  buttons.forEach(function (b) {
    var n = String(b.text).replace(/\D/g, '');
    var bdata = String(b.callback_data || '');
    var act = bdata.split(':')[0];
    var k = bdata.slice(act.length + 1);
    if (!listed[n]) return;
    var state = act === 'u' ? 'done' : act === 'x' ? 'gone' : 'open';
    if (k === key) state = action === 'd' ? 'done' : 'open';
    rows.push({n: n, key: k, title: listed[n].title, when: listed[n].when, state: state});
  });

  var out = render(lines[0], rows);
  telegram('editMessageText', {chat_id: msg.chat.id, message_id: msg.message_id, text: out.text,
                               parse_mode: 'HTML', reply_markup: {inline_keyboard: out.keyboard}});
}

/** The same message render() in telegram_checklist.py draws. */
function render(head, rows) {
  var lines = [esc(head), ''];
  var buttons = [];
  rows.forEach(function (r) {
    if (r.state === 'done') {
      lines.push('☑ ' + r.n + '  <s>' + esc(r.title) + ' · ' + esc(r.when) + '</s>');
      buttons.push({text: '✓' + r.n, callback_data: 'u:' + r.key});
    } else if (r.state === 'gone') {
      lines.push('✕ ' + r.n + '  ' + esc(r.title) + ' · not in the vault');
      buttons.push({text: '✕' + r.n, callback_data: 'x'});
    } else {
      lines.push('☐ ' + r.n + '  ' + esc(r.title) + ' · ' + esc(r.when));
      buttons.push({text: String(r.n), callback_data: 'd:' + r.key});
    }
  });
  lines.push('', esc(FOOTER));
  var keyboard = [];
  for (var i = 0; i < buttons.length; i += PER_ROW) keyboard.push(buttons.slice(i, i + PER_ROW));
  return {text: lines.join('\n'), keyboard: keyboard};
}

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/** Hand one update to the vault's workflow. True when GitHub accepted it. */
function dispatch(update) {
  var res = UrlFetchApp.fetch(
    'https://api.github.com/repos/' + props.getProperty('GITHUB_REPO') + '/dispatches', {
      method: 'post',
      contentType: 'application/json',
      muteHttpExceptions: true,
      headers: {
        Authorization: 'Bearer ' + props.getProperty('GITHUB_TOKEN'),
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
      },
      payload: JSON.stringify({event_type: 'telegram-update', client_payload: {update: update}})
    });
  if (res.getResponseCode() === 204) return true;
  console.error('GitHub refused update ' + update.update_id + ': ' + res.getResponseCode() + ' ' +
                res.getContentText().slice(0, 300));
  return false;
}

/**
 * Retry updates GitHub refused. Telegram has already let go of them, so they are kept here,
 * one property each, until GitHub takes them. Runs before each new update and hourly.
 */
function flushBacklog() {
  var all = props.getProperties();
  Object.keys(all).sort().forEach(function (k) {
    if (k.indexOf('pending_') !== 0) return;
    try {
      if (dispatch(JSON.parse(all[k]))) props.deleteProperty(k);
    } catch (err) {
      console.error('Backlog retry failed: ' + err);
    }
  });
}

function telegram(method, payload) {
  var res = UrlFetchApp.fetch(
    'https://api.telegram.org/bot' + props.getProperty('TELEGRAM_TOKEN') + '/' + method, {
      method: 'post', contentType: 'application/json', muteHttpExceptions: true,
      payload: JSON.stringify(payload)
    });
  return JSON.parse(res.getContentText());
}

/** Run once from the editor, after deploying and adding the properties. */
function setUpWebhook() {
  var url = props.getProperty('WEB_APP_URL');
  if (!url) throw new Error('Add WEB_APP_URL first: Deploy > Manage deployments > copy the URL.');
  var key = props.getProperty('WEBHOOK_KEY') || Utilities.getUuid().replace(/-/g, '');
  props.setProperty('WEBHOOK_KEY', key);
  var res = telegram('setWebhook', {
    url: url + '?key=' + key,
    allowed_updates: ['message', 'channel_post', 'callback_query']
  });
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'flushBacklog') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('flushBacklog').timeBased().everyHours(1).create();
  Logger.log(res.ok ? 'Webhook set. Telegram now pushes updates here.' : 'Telegram refused: ' + res.description);
}

/** Back to draining: Telegram holds updates again until telegram_capture.py --once fetches them. */
function removeWebhook() {
  var res = telegram('deleteWebhook', {});
  Logger.log(res.ok ? 'Webhook removed. Updates are drained again.' : 'Telegram refused: ' + res.description);
}

/** What Telegram reports about the webhook: pending updates and the last delivery error. */
function checkWebhook() {
  var info = telegram('getWebhookInfo', {}).result || {};
  Logger.log('Set: ' + Boolean(info.url) + '. Waiting: ' + (info.pending_update_count || 0) +
             '. Last error: ' + (info.last_error_message || 'none'));
}
