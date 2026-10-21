/**
 * Morning delivery for the loose-ends brief.
 *
 * The brief is written on Friday and Sunday evening, by the laptop or by the vault's Brief
 * workflow on GitHub, and mailed to you with
 * [WEEKLY BRIEF] in the subject. The 06:00 catch-up may queue a revised copy over it; the
 * newest tagged message is the one that goes out. A Gmail filter on that text archives it, so it never
 * reaches the inbox. This script runs on Google's servers at 07:00 on Saturday and Monday,
 * finds the queued brief, sends it on without the tag, and moves that copy into the inbox.
 *
 * The point is that Google does the delivering, whatever the writer was doing at seven.
 *
 * Nothing here deletes anything: a released brief is labelled rather than trashed, and the
 * label is also what stops it being sent twice.
 */

var QUEUE_TAG = '[WEEKLY BRIEF]';
// Quoted, so Gmail matches the phrase rather than the two words anywhere in a subject.
// A released brief is titled 'Morning Brief' or 'Weekend Brief' and so cannot match this
// and be collected again. The X-Brain-Queued check below is the backstop if it ever could.
var SEARCH = 'subject:"weekly brief" newer_than:3d -label:brief-released';
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
  // getEffectiveUser, not getActiveUser. Under a time-driven trigger there may be no active
  // user, and getActiveUser().getEmail() can then return an empty string, which would send
  // the release to nobody while still reporting success.
  var to = Session.getEffectiveUser().getEmail();

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

  // A brief sent to yourself can come back archived: Gmail may file it into the queued copy's
  // conversation, which the filter already took out of the inbox, or the filter can catch it
  // on arrival. Either way it sat under brief-released and never reached the inbox. A filter
  // acts only on arrival, so moving the conversation afterwards sticks.
  var moved = toInbox(subject);
  Logger.log('released: ' + subject + ' (' + threads.length + ' queued thread(s) cleared, ' +
             moved + ' moved to the inbox)');
}

/**
 * Move the released copy's conversation to the inbox, unread.
 *
 * It is found by its subject without the tag, so a queued copy in a conversation of its own
 * stays where the filter put it. Sent mail can take a few seconds to become searchable, hence
 * the retries. Returns the number of conversations moved; 0 in the log means it never showed.
 */
function toInbox(subject) {
  // Punctuation out: Gmail ignores it in a phrase search, and a quote would end the phrase.
  var phrase = subject.replace(/[^\w\s]/g, ' ').replace(/\s+/g, ' ').trim();
  var query = 'from:me subject:"' + phrase + '" -subject:"weekly brief" newer_than:1d';
  for (var attempt = 0; attempt < 6; attempt++) {
    var found = GmailApp.search(query, 0, 5);
    if (found.length) {
      GmailApp.moveThreadsToInbox(found);
      GmailApp.markThreadsUnread(found);
      return found.length;
    }
    Utilities.sleep(5000);
  }
  return 0;
}

/**
 * The newest message that send_brief.py actually queued.
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
