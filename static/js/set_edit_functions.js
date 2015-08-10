$(document).ready(function () {
    var container = $('#object_container');
    var modal = "";
    var delete_url = "";
    var load_url = "";
    var sortable = false;

    set_title('#content_title', $('#get_content_title').text());

    //init_sortable();

    $(document).on('click', '.btn-edit-order', function () {
        init_sortable();
        var button = $(this);
        button.toggleClass('btn-default btn-primary');
        button.toggleClass('btn-edit-order btn-save-order');
        button.text('Lagre Rekkefølge');
    });

    $(document).on('click', '.btn-save-order', function() {
        $('.sortable').sortable({
            disabled: true
        });
        var button = $(this);
        button.toggleClass('btn-default btn-primary');
        button.toggleClass('btn-save-order btn-edit-order');
        save_changes();
        button.html('Endre Rekkefølge')
        $('#order_success').fadeIn().delay(500).fadeOut();
    });

    // Open delete confirmation modal
    $(document).on('click', '.btn-delete-object', function () {
        modal = $('#deleteModal');
        var button = $(this);
        var object_id = button.data('object-id');
        var object_title = button.data('object-title');
        var object_type = button.data('object-type');

        if (object_type == 'set') {
            delete_url = '/set/' + object_id + '/remove/';
            load_url = '/user/sets/ #object_container > *';
        } else if (object_type == "chapter") {
            delete_url = '/set/' + current_set + '/chapter/' + object_id + '/remove/';
            load_url = '/set/' + current_set + '/chapters/ #object_container > *';
        } else if (object_type == "level") {
            delete_url = '/chapter/' + current_chapter + '/level/' + object_id + '/remove/';
            load_url = '/chapter/' + current_chapter + '/levels/ #object_container > *'
        } else if (object_type == "template") {
            delete_url = '/level/' + current_level + '/template/' + object_id + '/remove';
            load_url = '/level/' + current_level + '/templates/ #object_container > *'
        } else {
            console.log('Error: Requested object has no type.');
        }

        modal.find('.modal-alert').text('Bekreft sletting av "' + object_title + '."');
        console.log('opening confirm deletion modal for object-id: ' + object_id);
        console.log('current deletion url is: ' + delete_url);
        modal.modal('show');
    });

    // Confirm deletion of object ( Modal delete button )
    $(document).on('click', '#confirmDelete', function () {

        $.post(delete_url, {'csrfmiddlewaretoken': getCookie('csrftoken')}, function (result) {
            $('#deleteModal').modal('hide');
            //$(document).find('#object_id_' + del_object_id).effect("drop", "fast");
            container.load(load_url);
            init_sortable();
            window.console.log(result);
        });

    });

    $(document).on('click', '.btn-edit-title', function() {
        modal = $('#titleModal');
        console.log(modal);
        modal.modal('show');
    });

    $(document).on('focusout', 'newtitle', function() {
       title = $('newtitle').val();
        console.log(title);
    });

    $('.hidemodal').click(function () {
        console.log('closing modal: ' + modal);
        modal.modal('hide');
        //delete_content($(this).closest('li'));
    });

    // Save changes
    $('#btn_update').click(function (e) {
        e.preventDefault();
        save_changes();
    });

    // Adding new content from the input-field. Posting to server.
    $(document).on('focusout', '.new_content', function () { //TODO: make grid element if in grid-view.
        add_new_content($(this));
    }).on('keyup', '.new_content', function (e) {
        if (/(13)/.test(e.which)) $(this).focusout(); // Add chapter if one of these keys are pressed.
    });

    // Sends the search-query when either the search-button or 'enter' key is pressed.
    $(document).on('click', '#search_submit', function () {
        search_for($('#search_input').val());
        load_search_results();
    }).on('keyup', '#search_input', function (e) {
        if (/(13)/.test(e.which)) $('#search_submit').click();
    });

    $(document).on('click','.btn-copy-object', function() {
        var button = $(this);
        var add_url = "";
        var object_type = button.data('object-type');
        var object_id = button.data('object-id');
        if (object_type == 'set') {
            add_url = '/set/' + object_id + '/add/';
            load_url = '/user/sets/ #object_container > *';
        } else { console.log('not yet'); }

        $.post(add_url, {'csrfmiddlewaretoken': getCookie('csrftoken')}, function (result) {
            console.log(result);
            container.load(load_url);
        });

    });

    $(document).on('click', '.btn-add', function () {
        add_new_content_from_search($(this).attr('id').replace(/search_content_/g, ''));
    });

    init_k_factor_slider();
});

function add_new_content_from_search(content_id) {
    $.get($('#search_url_' + content_id).text(), function (result) {
        window.console.log(result);

        $('#object_container').load(window.location.pathname + "#object_container > *");
    });
}

/**
 * Saves changes such as content-order and content-title to the server.
 */
function save_changes() {
    var valid_form = true;
    var form_submit = {};
    var title = $('#current_content_title').text();
    var order = get_content_order();
    var content = $('#object_container');
    if (content.hasClass('edit_chapters')) {
        content = 'set';
        form_submit['set_id'] = current_set;
        form_submit['title'] = title;
        form_submit['order'] = order;
    } else if (content.hasClass('edit_levels')) {
        content = 'chapter';
        form_submit['chapter_id'] = $('#chapter_id').text();
        form_submit['title'] = title;
        form_submit['order'] = order;
    } else if (content.hasClass('edit_templates')) {
        content = 'level';
        form_submit['level_id'] = $('#level_id').text();
        form_submit['title'] = title;
        form_submit['k_factor'] = $('#k_factor_amount').text();
    } else {
        window.console.log('#edit_container is missing a required class for POST.');
        valid_form = false;
    }
    if (valid_form) {
        form_submit["csrfmiddlewaretoken"] = getCookie('csrftoken');
        $.post('/' + content + '/update/', form_submit, function (result) {
            if (result[0] == 'S') {
                $('#update_text').text(result);
                $('#update_success').show(100).delay(5000).hide(100);
            }
            else {
                window.console.log('Failed to update: ' + result);
            }
        });
    }
}

/**
 * Iterates and write the order of the content to an Array.
 * @returns {String} The order represented as a String.
 */
function get_content_order() {
    var order = [];

    $('#object_container').find('.panel-default').each(function () {
        order.push($(this).data('object_id'));
    });
    return order.join(',');
}

/**
 * Init the slider which sets the progression-speed for the level.
 */
function init_k_factor_slider() {
    var k_value = $('#k_factor_amount').text();
    if (k_value == '') {
        k_value = 3;
    }
    $('#k_factor_slider').slider({
        value: k_value,
        min: 1,
        max: 8,
        step: 1,
        slide: function (event, ui) {
            $('#k_factor_amount').text(ui.value);
        }
    });
}

/**
 * Set the title of the set/chapter/level
 * @param {string} input - which input-field to write to.
 * @param {string} title - the title.
 */
function set_title(input, title) {
    $(input).val(title);
}

/**
 * Adding a new content depending on which container-type the user is active in. (Set/Chapter/Level)
 * @param {String} input - the input string that will be the title of the content.
 */
function add_new_content(input) {
    var container = $('#object_container');
    var load_url = "";
    var text = input.val();
    if (text) {
        var content_path = '/set/' + text + '/new_set/';
        load_url = '/user/sets/ #object_container > *';
        if (input.hasClass('input-chapter-name')) {
            content_path = '/set/' + current_set + '/' + text + '/new_chapter/';
            load_url = '/set/' + current_set + '/chapters/ #object_container > *'
        } else if (input.hasClass('input-level-name')) {
            content_path = '/chapter/' + current_chapter + '/' + text + '/new_level/';
            load_url = '/chapter/' + current_chapter + '/levels/ #object_container > *'
        }
        $.post(content_path, {'csrfmiddlewaretoken': getCookie('csrftoken')}, function (result) {
            console.log(result);
            container.load(load_url);
            init_sortable();
        });
    }
    input.val("");
}

/**
 * Delete the specific content.
 * @param {object} content - the content selector
 */
function delete_content(content) {
    var container = $('#edit_container');
    var content_id = content.attr('id').match(/\d+/);
    if (content_id) {
        var content_path = '/set/' + content_id + '/remove_set/';
        if (container.hasClass('edit_chapters')) {
            content_path = '/set/' + $('#set_id').text() + '/chapter/' + content_id + '/remove_chapter/';
        } else if (container.hasClass('edit_levels')) {
            content_path = '/chapter/' + $('#chapter_id').text() + '/level/' + content_id + '/remove_level/';
        }
        $.post(content_path, {'csrfmiddlewaretoken': getCookie('csrftoken')}, function (result) {
            if (result[0] == 's') { // if success, delete the visual content.
                content.remove();
            }
            window.console.log(result);
        });
    }
}

/**
 * Loads the search view, with the specific search-filter for each chapters/levels/templates.
 */
function load_search_results() { // TODO: make the search result load with AJAX.
    var search_container = $('.search_container');
    var type = search_container.attr('id').replace(/search_/g, "");
    switch (type) {
        case 'sets':
            search_container.load('/minisearch/chapters', function () {
                //callback function
                $('#search_input').attr("placeholder", "Søk etter oppgavesett...").blur()
            });
            break;
        case 'chapters':
            search_container.load('/minisearch/chapters', function () {
                //callback function
                $('#search_input').attr("placeholder", "Søk etter kapitler...").blur()
            });
            break;
        case 'levels':
            search_container.load('/minisearch/levels', function () {
                //callback function
                $('#search_input').attr("placeholder", "Søk etter nivå...").blur()
            });
            break;
        case 'templates':
            search_container.load('/minisearch/templates', function () {
                //callback function
                $('#search_input').attr("placeholder", "Søk etter oppgavemaler...").blur()
            });
            break;
    }
}

/**
 * Initialize the drag-and-drop functionality for the listed contents. Sortable.
 */
function init_sortable() {
    //TODO: make it switchable (from list to grid)
    sortable = true;
    var container = $('.sortable');
    container.sortable({
        disabled: false,
        placeholder: "list_content_highlight",
        containment: "#object_container",
        axis: "y",
        cursor: "move"
    }).disableSelection();

    //$('#chapter_container').sortable({containment:"#chapter_container"}).disableSelection();
    //$('.list_chapter').draggable({containment:"#chapter_container", axis:"y"});
}

function disable_sortable() {}

function search_for(search_string) {
    var search_container = $('.search_container');
    var type = search_container.attr('id').replace(/search_/g, "");
    search_container.load('/minisearch/' + type + '?q=' + search_string + ' .search_container > *', function (result) {
        search_container.html(result);
        search_container.show("fade", {'direction': 'up'});
    });
}

function refresh_navbar_breadcrumb() {
    var breadcrumb_container = $('#navbar_current_sets');
    breadcrumb_container.load('/ajax/currentsets/refresh/', function (result) {
        breadcrumb_container.html(result);
    });
}


/**
 *Gets a cookie and returns its value
 * @param {string} name - the name of the cookie to get.
 * @returns {string} - Returns the value of the cookie specified.
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}