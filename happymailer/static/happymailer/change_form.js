var components = [
  'mj-button',
  'mj-container',
  'mj-column',
  'mj-section',
  'mj-text',
  'mj-hero',
  'mj-link',
  'mj-divider'
];

var tags = {
  '!top': components,
  '!attrs': {
    'font-size': null
  },
  'mj-section': {
    attrs: {
      'full-width': ['full-width']
    }
  },
  'mj-text': {
    attrs: {
      'color': null,
      'padding-left': null,
      'padding-right': null,
      'padding-top': null,
      'padding-bottom': null,
      'padding': null
    }
  },
  'mj-button': {
    attrs: {
      href: null,
      'background-color': null
    }
  }
};

components.forEach(function(name) {
  if (!tags[name]) {
    tags[name] = {};
  }
  tags[name].children = components.slice();
});

tags['mj-hero'].children = ['mj-hero-content'];

CodeMirror.defineMode('django', function(config) {
  var htmlBase = CodeMirror.getMode(config, 'xml');
  var djangoInner = CodeMirror.getMode(config, 'django:inner');
  return CodeMirror.overlayMode(htmlBase, djangoInner);
});

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = django.jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

django.jQuery.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  }
});

function completeAfter(cm, pred) {
  var cur = cm.getCursor();
  if (!pred || pred()) setTimeout(function() {
    if (!cm.state.completionActive)
      cm.showHint({ completeSingle: false });
  }, 100);
  return CodeMirror.Pass;
}

function completeIfAfterLt(cm) {
  return completeAfter(cm, function() {
    var cur = cm.getCursor();
    return cm.getRange(CodeMirror.Pos(cur.line, cur.ch - 1), cur) == "<";
  });
}

function completeIfInTag(cm) {
  return completeAfter(cm, function() {
    var tok = cm.getTokenAt(cm.getCursor());
    if (tok.type == "string" && (!/['"]/.test(tok.string.charAt(tok.string.length - 1)) || tok.string.length == 1)) return false;
    var inner = CodeMirror.innerMode(cm.getMode(), tok.state).state;
    return inner.tagName;
  });
}

django.jQuery(function($) {
  var body = document.getElementById('id_body');
  var width = body.offsetWidth;
  var cm = CodeMirror.fromTextArea(body, {
    lineNumbers: true,
    mode: 'django',
    tabSize: 2,
    electricChars: true,
    extraKeys: {
      "'<'": completeAfter,
      "'/'": completeIfAfterLt,
      "' '": completeIfInTag,
      "'='": completeIfInTag,
      "Ctrl-Space": "autocomplete"
    },
    hintOptions: { schemaInfo: tags },
    theme: 'solarized'
  });
  cm.setSize(width, 'auto');

  var previewBtn = $('#preview_btn');

  var previewContainer = $('#preview_container');

  function setPreview(err, response) {
    previewContainer.find('iframe').remove();
    var frame = $('<iframe seamless></iframe>');
    var html;
    if (err) {
      html = '<div style="color:red">' + (err.responseText || 'failure') + '</div>';
      $('.variable_value').empty();
    } else {
      html = response.html;
      $.each(response.variables, function(key, value) {
        $('[data-variable=' + key + ']').text(value);
      });
    }
    frame.attr('src', 'data:text/html;charset=utf-8,' + encodeURI(html));
    previewContainer.append(frame);
  }

  function updatePreview() {
    previewContainer.find('iframe').remove();
    $.post(previewBtn.data('url'), {
      layout: $('#id_layout').val(),
      template: previewBtn.data('template'),
      body: cm.getValue()
    }).then(function(response) {
      setPreview(null, response);
    }, function(err) {
      setPreview(err);
    });
  }

  previewBtn.click(function() {
    updatePreview();
    return false;
  });

  updatePreview();
});
