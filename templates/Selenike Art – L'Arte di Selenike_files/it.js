(function(global){var Language = {};

Language.pluralFormFunction = function (n) {
		if (n === 1) {
			return 'one';
		}

		return 'other';
	};


Language.bubble = Language.bubble || {};

Language.bubble.attention_grabber = {
	"message": "Attention grabber per la chat"
};


Language.chat = Language.chat || {};

Language.chat.Warning = {
	"message": "Avvertimento"
};
Language.chat.accept_call = {
	"message": "Accetta"
};
Language.chat.active = {
	"message": "Attivo"
};
Language.chat.agent_profile_image = {
	"message": "Foto profilo dell'agente"
};
Language.chat.agent_ringing = {
	"message": "Chiamata in arrivo"
};
Language.chat.all_conversations = {
	"message": "Vedi tutte le conversazioni"
};
Language.chat.call_end_details = {
	"message": "Iniziato alle #startedOn e durato #duration",
	"vars": [
		"startedOn",
		"duration"
	]
};
Language.chat.call_error_load = {
	"message": "Impossibile caricare i dettagli delle chiamate."
};
Language.chat.call_started_on = {
	"message": "Iniziato alle #startedOn",
	"vars": [
		"startedOn"
	]
};
Language.chat.chatEnded = {
	"message": "La tua chat è terminata"
};
Language.chat.chat_icon = {
	"message": "Icona della chat"
};
Language.chat.chat_qm = {
	"message": "Vuoi chattare?"
};
Language.chat.chat_text = {
	"message": "Chat"
};
Language.chat.close_icon = {
	"message": "Icona di chiusura"
};
Language.chat.completed_call = {
	"message": "Chiamata terminata"
};
Language.chat.conversation_ended_on = {
	"message": "Conversazione terminata il"
};
Language.chat.decline_call = {
	"message": "Rifiuta"
};
Language.chat.defaultName = {
	"message": "Tu (cambia nome)"
};
Language.chat.departmentIsAway = {
	"message": "Il reparto #strongStart #departmentName #strongEnd è al momento assente.",
	"vars": [
		"departmentName",
		"strongStart",
		"strongEnd"
	]
};
Language.chat.departmentIsOffline = {
	"message": "Il reparto #strongStart #departmentName #strongEnd è al momento offline. Potresti ricevere supporto da un altro reparto.",
	"vars": [
		"departmentName",
		"strongStart",
		"strongEnd"
	]
};
Language.chat.download = {
	"message": "Scarica"
};
Language.chat.downloadFile = {
	"message": "Scarica File"
};
Language.chat.dragDropText = {
	"message": "Trascina un file qui per caricarlo"
};
Language.chat.emoji_error_load = {
	"message": "Impossibile caricare emoji"
};
Language.chat.error_title = {
	"message": "Errore"
};
Language.chat.failed = {
	"message": "Fallito"
};
Language.chat.generalUploadError = {
	"message": "\"#fileName\", si prega di riprovare.",
	"vars": [
		"fileName"
	]
};
Language.chat.generalUploadErrorLabel = {
	"message": "Impossibile caricare il file"
};
Language.chat.goToLatest = {
	"message": "Messaggi più recenti"
};
Language.chat.hideButton = {
	"message": "Nascondi chat"
};
Language.chat.incoming_call_message = {
	"message": "Chiamata in arrivo da #name",
	"vars": [
		"name"
	]
};
Language.chat.insert_emoji = {
	"message": "Inserisci emoji"
};
Language.chat.justNow = {
	"message": "proprio ora"
};
Language.chat.limit2 = {
	"message": "La dimensione massima per un file è di 2MB per i browser mobili, si prega di caricare un file più piccolo."
};
Language.chat.limit50 = {
	"message": "La dimensione massima per un file è di 50MB, si prega di caricare un file più piccolo."
};
Language.chat.message_not_delivered = {
	"message": "Il messaggio non è stato consegnato, clicca qui per inviarlo nuovamente."
};
Language.chat.message_too_long = {
	"message": "Il Messaggio non può superare i 5000 caratteri"
};
Language.chat.missed_agent = {
	"message": "La tua chiamata è stata persa"
};
Language.chat.missed_visitor = {
	"message": "Hai perso una chiamata"
};
Language.chat.missed_visitor_messagePreview = {
	"message": "Hai perso una chiamata da"
};
Language.chat.mobileName = {
	"message": "Tu"
};
Language.chat.newChat = {
	"message": "Inizia una nuova chat"
};
Language.chat.newMessages = {
	"message": "Nuovi messaggi"
};
Language.chat.new_conversation = {
	"message": "Nuova conversazione"
};
Language.chat.notificationTitle = {
	"message": "notifica"
};
Language.chat.ongoing_call = {
	"message": "Chiamata in corso"
};
Language.chat.past = {
	"message": "#time fa",
	"vars": [
		"time"
	]
};
Language.chat.pasted_image_title = {
	"message": "Immagine incollata alle #dateTime",
	"vars": [
		"dateTime"
	]
};
Language.chat.profile_prechat_text = {
	"message": "Compila il modulo di seguito per iniziare a parlare con me."
};
Language.chat.rejected_call = {
	"message": "Hai rifiutato questa chiamata"
};
Language.chat.remove_rate = {
	"message": "Hai rimosso la tua valutazione a questa chat"
};
Language.chat.resend = {
	"message": "Rinviare"
};
Language.chat.retry = {
	"message": "Riprova."
};
Language.chat.return_to_live_chat = {
	"message": "Torna alla Chat"
};
Language.chat.say_something = {
	"message": "Scrivi una risposta.."
};
Language.chat.screen_share_error = {
	"message": "Condivisione dello schermo non disponibile."
};
Language.chat.send_mail = {
	"message": "Invia email"
};
Language.chat.sent_file = {
	"message": "Invia un file"
};
Language.chat.sent_form = {
	"message": "Sent a form"
};
Language.chat.sent_suggested_message = {
	"message": "Sent a suggested message"
};
Language.chat.today_time = {
	"message": "Oggi, #time",
	"vars": [
		"time"
	]
};
Language.chat.tryAgain = {
	"message": "Prova di nuovo."
};
Language.chat.unanswered = {
	"message": "Senza risposta"
};
Language.chat.uploading = {
	"message": "Caricamento..."
};
Language.chat.video_call_error = {
	"message": "Videochiamata non disponibile."
};
Language.chat.visitor_ringing = {
	"message": "Chiama..."
};
Language.chat.voice_call_error = {
	"message": "Chiamata vocale non disponibile."
};
Language.chat.we_are_live = {
	"message": "Siamo online e pronti a parlare con te. Scrivi qualcosa per iniziare una chat in tempo reale."
};


Language.days = Language.days || {};

Language.days['0'] = {
	"message": "Domenica"
};
Language.days['1'] = {
	"message": "Lunedì"
};
Language.days['2'] = {
	"message": "Martedì"
};
Language.days['3'] = {
	"message": "Mercoledì"
};
Language.days['4'] = {
	"message": "Giovedì"
};
Language.days['5'] = {
	"message": "Venerdì"
};
Language.days['6'] = {
	"message": "Sabato"
};


Language.form = Language.form || {};

Language.form.CancelButton = {
	"message": "Annulla"
};
Language.form.CloseButton = {
	"message": "Chiudi"
};
Language.form.DepartmentsErrorMessage = {
	"message": "Deve essere indicato il reparto."
};
Language.form.DepartmentsPlaceholder = {
	"message": "seleziona il reparto.."
};
Language.form.EmailErrorMessage = {
	"message": "Indirizzo email non valido"
};
Language.form.EmailPlaceholder = {
	"message": "Indirizzo e-mail"
};
Language.form.EmailTranscriptFormMessage = {
	"message": "Per favore compila il modulo sottostante per ricevere questa chat al tuo indirizzo email."
};
Language.form.EmailTranscriptSuccess = {
	"message": "Richiesta di trascrizione email inviata."
};
Language.form.EmailTranscriptTo = {
	"message": "Invia chat a"
};
Language.form.EndChatMessage = {
	"message": "Grazie per aver chattato con noi. Sentiti libero di iniziare una nuova sessione di chat oppure inserisci la tua email e invia una trascrizione di questa conversazione alla tua casella di posta."
};
Language.form.EndChatMessage2 = {
	"message": "Grazie per aver conversato con noi. Sentiti libero di iniziare una nuova chat in qualsiasi momento."
};
Language.form.subject = {
	"message": "Oggetto"
};
Language.form.RequestSent = {
	"message": "La tua richiesta è stata inviata"
};
Language.form.EndChatTitle = {
	"message": "Sei sicuro di voler terminare questa chat?"
};
Language.form.MessagePlaceholder = {
	"message": "il tuo messaggio..."
};
Language.form.NameErrorMessage = {
	"message": "Il nome deve essere indicato."
};
Language.form.NameFormMessage = {
	"message": "Per favore cambia il tuo nome così possiamo riconoscerti la prossima volta."
};
Language.form.OfflineFormMessage = {
	"message": "Per favore compila il form sottostante e ti ricontatteremo al più presto possibile."
};
Language.form.OfflineMessageNotSent = {
	"message": "Il tuo messaggio non è stato consegnato, riprova"
};
Language.form.OfflineMessageSent = {
	"message": "Il tuo messaggio è stato inviato con successo!"
};
Language.form.PhoneErrorMessage = {
	"message": "Numero di telefono non valido"
};
Language.form.PreChatFormMessage = {
	"message": "Per favore compila il modulo sotto per iniziare a chattare con il primo agente disponibile."
};
Language.form.PreChatFormMessageProfile = {
	"message": "Per favore compila il modulo sotto per iniziare a chattare con #name."
};
Language.form.QuestionPlaceholder = {
	"message": "tua domanda.."
};
Language.form.RequiredErrorMessage = {
	"message": "Questo campo è obbligatorio"
};
Language.form.SaveButton = {
	"message": "Salva"
};
Language.form.SendButton = {
	"message": "Invia"
};
Language.form.SendMessage = {
	"message": "Invia messaggio"
};
Language.form.StartChatButton = {
	"message": "Inizia chat"
};
Language.form.SubmitButton = {
	"message": "Invia"
};
Language.form.SubmittedFrom = {
	"message": "Inviato da"
};
Language.form.SubmittingProcess = {
	"message": "Invio in corso"
};
Language.form.TranscriptMessage = {
	"message": "Sentiti libero di inserire la tua email e inviare una trascrizione di questa chat alla tua casella di posta."
};
Language.form.any = {
	"message": "Qualsiasi"
};
Language.form.chatEnded = {
	"message": "La tua chat è terminata"
};
Language.form.department = {
	"message": "Reparto"
};
Language.form.email = {
	"message": "Indirizzo email"
};
Language.form.errorSaving = {
	"message": "Impossibile salvare. Per favore riprova"
};
Language.form.message = {
	"message": "Messaggio"
};
Language.form.name = {
	"message": "Nome"
};
Language.form.sendAgain = {
	"message": "Invia di nuovo"
};
Language.form.visitButton = {
	"message": "Visita tawk.to"
};


Language.home = Language.home || {};

Language.home.banner_image = {
	"message": "Immagine del banner"
};
Language.home.chat_button = {
	"message": "Nuova conversazione"
};
Language.home.chat_input = {
	"message": "Scrivi qui e premi invio..."
};
Language.home.heading_main = {
	"message": "Ciao #twkWake"
};
Language.home.heading_sub = {
	"message": "Hai bisogno d'aiuto? Cerca le risposte nel nostro centro assistenza oppure inizia una conversazione:"
};
Language.home.kb_search = {
	"message": "Ricerca risposte"
};
Language.home.logo_image = {
	"message": "Immagine del logo"
};


Language.kb = Language.kb || {};

Language.kb.article_image = {
	"message": "Immagine dell'articolo"
};
Language.kb.article_rating = {
	"message": "L'articolo ti è stato d'aiuto?"
};
Language.kb.article_rating_count = {
	"message": "A #totalLikes su #totalVotes è piaciuto quest'articolo",
	"vars": [
		"totalLikes",
		"totalVotes"
	]
};
Language.kb.author_profile_image = {
	"message": "Immagine profilo dell'autore"
};
Language.kb.clear_search = {
	"message": "Pulisci la ricerca"
};
Language.kb.downvote_rating_button = {
	"message": "No"
};
Language.kb.help_center = {
	"message": "Supporto"
};
Language.kb.negative_rating = {
	"message": "Negativo"
};
Language.kb.positive_rating = {
	"message": "Positivo"
};
Language.kb.recent_searches = {
	"message": "Ricerche recenti"
};
Language.kb.search_fail_description = {
	"message": "Per favore, riprova"
};
Language.kb.search_fail_title = {
	"message": "Nessun risultato"
};
Language.kb.search_placeholder = {
	"message": "Ricerca risposte"
};
Language.kb.search_results = {
	"message": "Risultati della ricerca"
};
Language.kb.show_all_results = {
	"message": "Mostra tutti i risultati (#num)",
	"vars": [
		"num"
	]
};
Language.kb.submit_search = {
	"message": "Invia ricerca"
};
Language.kb.upvote_rating_button = {
	"message": "Si"
};
Language.kb.view_full = {
	"message": "Visualizza per intero"
};


Language.menu = Language.menu || {};

Language.menu.add_chat_to_your_website = {
	"message": "Aggiungi le Chat al tuo sito web"
};
Language.menu.change_name = {
	"message": "Cambia Nome"
};
Language.menu.email_transcript = {
	"message": "Trascrizione e-mail"
};
Language.menu.end_chat_session = {
	"message": "Termina questa sessione di chat"
};
Language.menu.popout_widget = {
	"message": "Widget pop-out"
};
Language.menu.sound_off = {
	"message": "Suoni Disattivati"
};
Language.menu.sound_on = {
	"message": "Suoni Attivati"
};


Language.months = Language.months || {};

Language.months['0'] = {
	"message": "Gennaio"
};
Language.months['1'] = {
	"message": "Febbraio"
};
Language.months['10'] = {
	"message": "Novembre"
};
Language.months['11'] = {
	"message": "Dicembre"
};
Language.months['2'] = {
	"message": "Marzo"
};
Language.months['3'] = {
	"message": "Aprile"
};
Language.months['4'] = {
	"message": "Maggio"
};
Language.months['5'] = {
	"message": "Giugno"
};
Language.months['6'] = {
	"message": "Luglio"
};
Language.months['7'] = {
	"message": "Agosto"
};
Language.months['8'] = {
	"message": "Settembre"
};
Language.months['9'] = {
	"message": "Ottobre"
};


Language.notifications = Language.notifications || {};

Language.notifications.dismiss_alert = {
	"message": "Ignora avviso"
};
Language.notifications.maximum_file_upload_warning = {
	"message": "Spiacenti, il trasferimento di file è limitato a #limitFileNumber file alla volta. Si prega di provare il seguente(i) file di nuovo :",
	"vars": [
		"limitFileNumber"
	]
};
Language.notifications.maximum_size_upload_warning = {
	"message": "Spiacenti, il trsferimento di file è limitato a #limitFileSize per file. Si prega di comprimere il seguente(i) file e riprovare.",
	"vars": [
		"limitFileSize"
	]
};
Language.notifications.reconnecting = {
	"message": "Riconnessione in corso"
};
Language.notifications.retry = {
	"message": "Riprova"
};


Language.overlay = Language.overlay || {};

Language.overlay.cookiesOff = {
	"message": "Non puoi usare questa chat perché i cookie sono disattivati su questo browser. Si prega di attivarli e ricaricare la pagina."
};
Language.overlay.inactive = {
	"message": "Clicca qui per riavviare la chat"
};
Language.overlay.maintenance = {
	"message": "La chat è in manutenzione"
};
Language.overlay.tawkContent = {
	"message": "Questo widget è realizzato da tawk.to - un'applicazione di messaggistica gratuita che ti permette di monitorare e interagire con i visitatori del tuo sito web."
};


Language.rollover = Language.rollover || {};

Language.rollover.back = {
	"message": "Indietro"
};
Language.rollover.chatMenu = {
	"message": "Menu"
};
Language.rollover.emailTranscriptOption = {
	"message": "Trascrizione via email"
};
Language.rollover.end = {
	"message": "Termina la chat"
};
Language.rollover.knowledgeBase = {
	"message": "Knowledge Base"
};
Language.rollover.maximize = {
	"message": "Ingrandisci"
};
Language.rollover.minimize = {
	"message": "Riduci"
};
Language.rollover.negativeRating = {
	"message": "Valuta questa chat con -1"
};
Language.rollover.popOut = {
	"message": "Apri in un'altra finestra"
};
Language.rollover.positiveRating = {
	"message": "Valuta questa chat con +1"
};
Language.rollover.rateChat = {
	"message": "Valuta questa chat"
};
Language.rollover.resendMessage = {
	"message": "Re-invia il messaggio"
};
Language.rollover.resize = {
	"message": "Ridimensiona"
};
Language.rollover.screenShare = {
	"message": "Condivisione Schermo"
};
Language.rollover.uploadFile = {
	"message": "Carica File"
};
Language.rollover.videoCall = {
	"message": "Videochiamata"
};
Language.rollover.voiceCall = {
	"message": "Chiamata Vocale"
};


Language.routes = Language.routes || {};

Language.routes.all_agents = {
	"message": "Tutti gli agenti"
};
Language.routes.conversations = {
	"message": "Conversazioni"
};
Language.routes.load_more = {
	"message": "Carica altro"
};


Language.status = Language.status || {};

Language.status.away = {
	"message": "Assente"
};
Language.status.offline = {
	"message": "Offline"
};
Language.status.online = {
	"message": "Online"
};




Language.chat = Language.chat || {};

Language.chat.hours = {
	"pluralVars": [
		"num"
	],
	"message": {
		"one": "#num ora",
		"other": "#num ore"
	}
};
Language.chat.messageQueuedText = {
	"pluralVars": [
		"t"
	],
	"message": {
		"one": "Il tempo di attesa stimato è di #strongStart #t minuto #strongEnd",
		"other": "Il tempo di attesa stimato è di #strongStart #t minuti #strongEnd"
	},
	"vars": [
		"strongStart",
		"strongEnd"
	]
};
Language.chat.minutes = {
	"pluralVars": [
		"num"
	],
	"message": {
		"one": "#num minuto",
		"other": "#num minuti"
	}
};
Language.chat.newMessage = {
	"pluralVars": [
		"num"
	],
	"message": {
		"one": "#num nuovo messaggio",
		"other": "#num nuovi messaggi"
	}
};
Language.chat.seconds = {
	"pluralVars": [
		"num"
	],
	"message": {
		"one": "#num secondo",
		"other": "#num secondi"
	}
};


global.$_Tawk.language = Language;})(window);