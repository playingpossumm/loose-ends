/**
 * Morning delivery for the loose-ends brief.
 *
 * The laptop writes the brief on Friday and Sunday evening and mails it to you with
 * [BRIEF-QUEUED] in the subject. The 06:00 catch-up may queue a revised copy over it; the
 * newest tagged message is the one that goes out. A Gmail filter on that text archives it, so it never
 * reaches the inbox. This script runs on Google's servers at 07:00 on Saturday and Monday,
 * finds the queued brief, and sends it on without the tag.
 *
 * The point is that Google does the delivering. The laptop can be shut, asleep, or in a bag.
 *
 * Nothing here deletes anything: a released brief is labelled rather than trashed, and the
 * label is also what stops it being sent twice.
 */

var QUEUE_TAG = '[BRIEF-QUEUED]';
var SEARCH = 'subject:(BRIEF-QUEUED) newer_than:3d -label:brief-released';
var RELEASED_LABEL = 'brief-released';

/** Send the newest queued brief, if there is one. Silent when there is not. */
function releaseBrief() {
  var threads = GmailApp.search(SEARCH, 0, 5);
  if (!threads.length) {
    Logger.log('nothing queued — done');
    return;
  }

  var message = newestQueuedMessage(threads);
  if (!message) {
    Logger.log('found threads but no message carrying X-Brain-Queued — done');
    return;
  }

  var subject = message.getSubject().replace(QUEUE_TAG, '').trim();
  var to = Session.getActiveUser().getEmail();

  GmailApp.sendEmail(to, subject, message.getPlainBody(), {
    htmlBody: message.getBody(),
    name: 'loose-ends'
  });

  // Label every thread the search matched, not only the one released. A revision queued in
  // the morning leaves the night's copy behind it, and an unlabelled copy inside the
  // three-day window could otherwise be picked up by the next trigger.
  var released = label(RELEASED_LABEL);
  for (var i = 0; i < threads.length; i++) {
    released.addToThread(threads[i]);
  }
  Logger.log('released: ' + subject + ' (' + threads.length + ' queued thread(s) cleared)');
}

/**
 * The newest message that the laptop actually queued.
 *
 * The subject search is what Gmail can match; the header is what proves the message came
 * from send_brief.py rather than from anything else that happened to use the words.
 */
function newestQueuedMessage(threads) {
  var found = null;
  for (var i = 0; i < threads.length; i++) {
    var messages = threads[i].getMessages();
    for (var j = 0; j < messages.length; j++) {
      var m = messages[j];
      if (m.getSubject().indexOf(QUEUE_TAG) === -1) continue;
      if (m.getRawContent().indexOf('X-Brain-Queued: 1') === -1) continue;
      if (!found || m.getDate() > found.getDate()) found = m;
    }
  }
  return found;
}

function label(name) {
  return GmailApp.getUserLabelByName(name) || GmailApp.createLabel(name);
}

/**
 * Install the two triggers. Run once, from the editor, and again only to change the times.
 *
 * Apps Script fires an hourly trigger inside its hour rather than on the minute; nearMinute
 * narrows that to roughly a quarter of an hour either side of seven.
 */
function setUpTriggers() {
  var existing = ScriptApp.getProjectTriggers();
  for (var i = 0; i < existing.length; i++) {
    if (existing[i].getHandlerFunction() === 'releaseBrief') {
      ScriptApp.deleteTrigger(existing[i]);
    }
  }

  var days = [ScriptApp.WeekDay.SATURDAY, ScriptApp.WeekDay.MONDAY];
  for (var d = 0; d < days.length; d++) {
    ScriptApp.newTrigger('releaseBrief')
      .timeBased()
      .onWeekDay(days[d])
      .atHour(7)
      .nearMinute(0)
      .create();
  }
  Logger.log('triggers installed: Saturday and Monday, 07:00 ' + Session.getScriptTimeZone());
}

/** Run by hand to check the wiring without waiting for Saturday. */
function testRelease() {
  releaseBrief();
}
