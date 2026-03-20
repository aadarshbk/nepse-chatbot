// // static/js/script.js

// /* ── Theme ───────────────────────────────────────────────────────────────── */
// window.toggleTheme = function () {
//     var current = localStorage.getItem('tm_theme') || 'dark';
//     var next    = current === 'dark' ? 'light' : 'dark';
//     document.documentElement.setAttribute('data-theme', next);
//     localStorage.setItem('tm_theme', next);
// };

// (function () {
//     var t = localStorage.getItem('tm_theme') || 'dark';
//     document.documentElement.setAttribute('data-theme', t);
// })();


// document.addEventListener('DOMContentLoaded', function () {

//     var form      = document.getElementById('chat-form');
//     var input     = document.getElementById('msg-input');
//     var submitBtn = document.getElementById('send-btn');
//     var messages  = document.getElementById('messages');

//     scrollToBottom();
//     fetchMarketStatus();
//     setInterval(fetchMarketStatus, 60000);

//     /* ── Form submit ────────────────────────────────────────────────────── */
//     if (form) {
//         form.addEventListener('submit', function (e) {
//             var text = input.value.trim();
//             if (!text) { e.preventDefault(); return; }
//             showLoading(text);
//             submitBtn.disabled = true;
//         });
//     }

//     /* ── Wire up data-prompt elements (chips, sector cards, topic items) ── */
//     document.querySelectorAll('[data-prompt]').forEach(function(el) {
//         el.addEventListener('click', function() {
//             sendPrompt(this.dataset.prompt);
//         });
//     });

//     /* ── Loading bubbles ────────────────────────────────────────────────── */
//     function showLoading(text) {
//         var empty = document.getElementById('empty-state');
//         if (empty) empty.remove();

//         var u = document.createElement('div');
//         u.className = 'msg user';
//         u.innerHTML =
//             '<div class="msg-meta"><div class="avatar">U</div>You</div>' +
//             '<div class="msg-bubble">' + escapeHtml(text) + '</div>' +
//             '<button class="edit-btn" onclick="editMessage(\'' +
//                 text.replace(/\\/g,'\\\\').replace(/'/g,"\\'") +
//             '\')">✏ Edit</button>';
//         messages.appendChild(u);

//         var b = document.createElement('div');
//         b.className = 'msg bot';
//         b.innerHTML =
//             '<div class="msg-meta"><div class="avatar">TM</div>TradeMind</div>' +
//             '<div class="msg-bubble">' +
//                 '<div class="loading-dots">' +
//                     '<span class="ld"></span>' +
//                     '<span class="ld"></span>' +
//                     '<span class="ld"></span>' +
//                 '</div>' +
//             '</div>';
//         messages.appendChild(b);
//         scrollToBottom();
//     }

//     /* ── Quick prompts ──────────────────────────────────────────────────── */
//     window.sendPrompt = function (text) {
//         if (!input || !form) return;
//         input.value = text;
//         showLoading(text);
//         submitBtn.disabled = true;
//         form.submit();
//     };

//     /* ── Edit message ───────────────────────────────────────────────────── */
//     window.editMessage = function (text) {
//         input.value = text;
//         input.focus();
//         input.setSelectionRange(text.length, text.length);
//     };

//     /* ── Clear chat ─────────────────────────────────────────────────────── */
//     window.clearChat = async function () {
//         var sidEl = document.querySelector('input[name="session_id"]');
//         var sid   = sidEl ? sidEl.value : 'default';
//         try {
//             await fetch('/api/chat/history?session_id=' + encodeURIComponent(sid), {
//                 method: 'DELETE'
//             });
//         } catch (err) {
//             console.warn('Could not clear history:', err);
//         }
//         window.location.reload();
//     };

//     /* ── Market status ──────────────────────────────────────────────────── */
//     async function fetchMarketStatus() {
//         try {
//             var res  = await fetch('/api/market');
//             var data = await res.json();
//             var el   = document.getElementById('market-status');
//             if (el && data.status) el.textContent = data.status;
//         } catch (e) { /* silent */ }
//     }

//     /* ── Helpers ────────────────────────────────────────────────────────── */
//     function scrollToBottom() {
//         if (messages) messages.scrollTop = messages.scrollHeight;
//     }

//     function escapeHtml(s) {
//         return s
//             .replace(/&/g,  '&amp;')
//             .replace(/</g,  '&lt;')
//             .replace(/>/g,  '&gt;')
//             .replace(/"/g,  '&quot;');
//     }

// });