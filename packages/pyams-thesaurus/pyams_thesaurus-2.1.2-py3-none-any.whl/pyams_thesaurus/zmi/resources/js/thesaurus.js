/* global MyAMS */

'use strict';


if (window.$ === undefined) {
    window.$ = MyAMS.$;
}


const thesaurus = {

    /**
     * Module initialization
     *
     * Load module CSS on page load.
     */
    init: () => {
        let css = $('[data-ams-thesaurus-css]').data('ams-thesaurus-css');
        if (!css) {
            css = '/--static--/pyams_thesaurus/css/thesaurus.css';
        }
        MyAMS.core.getCSS(css, 'pyams_template').catch(() => {
            console.warning(`Can't load thesaurus CSS: ${css}`);
        });
    },

    /**
     * Thesaurus terms tree management
     */
    tree: {

        init: () => {
            $(document).off('click', 'i.extract-checker');
            $(document).on('click', 'i.extract-checker', (evt) => {
                const checker = $(evt.currentTarget);
                if (checker.hasClass('disabled')) {
                    return;
                }
                const term = $('span.term', checker.closest('div').siblings('span'));
                MyAMS.require('ajax').then(() => {
                    MyAMS.ajax.post('switch-extract.json', {
                        term: term.text(),
                        extract: checker.data('ams-extract-name')
                    }).then((data) => {
                        if (data.status) {  // System view
                            MyAMS.ajax.handleJSON(data);
                        } else if (data.used) {
                            $(`>li >div i.extract-checker[data-ams-extract-name="${data.extract}"]`,
                                checker.closest('div').siblings('ul.group'))
                                .replaceWith($('<i></i>').addClass('extract-checker far fa-fw fa-square')
                                                         .css('color', `#${data.color}`)
                                                         .attr('data-ams-extract-name', data.extract));
                            checker.replaceWith($(`<i></i>`).addClass('extract-checker fas fa-fw fa-square used')
                                                            .css('color', `#${data.color}`)
                                                            .attr('data-ams-extract-name', data.extract));
                        } else {
                            $(`i.extract-checker[data-ams-extract-name="${data.extract}"]`,
                                checker.closest('div').siblings('ul.group'))
                                .replaceWith($('<i></i>').addClass('extract-checker fas fa-fw fa-square disabled')
                                                         .css('color', 'silver')
                                                         .attr('data-ams-extract-name', data.extract));
                            checker.replaceWith($('<i></i>').addClass('extract-checker far fa-fw fa-square')
                                                            .css('color', `#${data.color}`)
                                                            .attr('data-ams-extract-name', data.extract));
                        }
                    });
                });
            });
        },

        /**
         * Search for selected term from search box
         * @param evt
         */
        search: (evt) => {
            const label = $(evt.currentTarget).val();
            if (label) {
                MyAMS.thesaurus.tree.findTerm(null, {term: label});
            }
        },

        /**
         * Display child nodes of a given term
         *
         * @param term
         * @param nodes
         * @param source
         */
        displaySubNodes: (term, nodes, source) => {
            if (source === undefined) {
                source = $(`span.term:withtext("${term}")`).siblings('i[data-ams-click-handler]');
            }
            const
                group = source.parents('span.label').siblings('ul.group'),
                parent = group.closest('ul.group').closest('li');
            group.empty();
            for (const node of nodes) {
                const li = $('<li></li>');
                node.extracts.reverse();
                for (const extract of node.extracts) {
                    const
                        div = $('<div></div>').addClass('float-right mr-2')
                                              .appendTo(li),
                        square = $('<i></i>').attr('data-ams-extract-name', extract.name)
                                             .addClass('fas fa-fw fa-square extract-checker')
                                             .css('color', `#${extract.color}`),
                        parentChecker = $(`>div i.extract-checker[data-ams-extract-name="${extract.name}"]`, parent);
                    if (parentChecker.hasClass('used')) {
                        if (extract.used) {
                            square.addClass('used');
                        } else {
                            square.removeClass('fas')
                                .addClass('far');
                        }
                        const
                            switcher = $('i.switcher', `table.extracts tr[data-ams-element-name="${extract.name}"]`),
                            svg = $('svg', switcher),
                            icon = svg.exists() ? svg : switcher;
                        if (!icon.hasClass('fa-eye')) {
                            square.css('visibility', 'hidden');
                        }
                    } else {
                        square.addClass('disabled')
                              .css('color', 'silver');
                    }
                    square.appendTo(div);
                }
                const span = $('<span></span>')
                    .addClass('label py-1')
                    .addClass(node.css_class)
                    .attr('data-ams-url', node.view)
                    .attr('data-toggle', 'modal');
                if (node.expand) {
                    $('<i></i>')
                        .addClass('fas fa-fw fa-plus-circle')
                        .attr('data-ams-click-handler', 'MyAMS.thesaurus.tree.expandOrCollapse')
                        .attr('data-ams-stop-propagation', true)
                        .appendTo(span);
                }
                $('<span></span>')
                    .addClass('term')
                    .html(node.label)
                    .appendTo(span);
                span.appendTo(li);
                if (node.extensions) {
                    for (const extension of node.extensions) {
                        if (extension.active) {
                            $('<i></i>')
                                .addClass(extension.icon)
                                .addClass('extension hint mx-2 my-1 float-right mouse-pointer')
                                .addClass('opaque text-primary')
                                .attr('data-ams-url', extension.view)
                                .attr('data-toggle', 'modal')
                                .attr('title', extension.title)
                                .appendTo(li);
                        } else {
                            $('<i></i>')
                                .addClass(extension.icon)
                                .addClass('extension hint mx-2 my-1 float-right mouse-pointer')
                                .addClass('text-secondary')
                                .attr('data-ams-click-handler', 'MyAMS.thesaurus.tree.switchExtension')
                                .attr('data-ams-extension-name', extension.name)
                                .attr('title', extension.title)
                                .appendTo(li);
                        }
                    }
                }
                $('<ul></ul>')
                    .addClass('hidden group')
                    .appendTo(li);
                li.appendTo(group);
                if (node.subnodes) {
                    MyAMS.thesaurus.tree.displaySubNodes(node.label, node.subnodes);
                }
            }
            group.removeClass('hidden');
            source.replaceWith($('<i></i>').addClass('fas fa-fw fa-minus-circle')
                                           .attr('data-ams-click-handler', 'MyAMS.thesaurus.tree.expandOrCollapse')
                                           .attr('data-ams-stop-propagation', 'true'));
        },

        /**
         * Switch thesaurus node
         */
        expandOrCollapse: (evt) => {
            let handler = $(evt.currentTarget);
            if (evt.currentTarget.tagName.toLowerCase() !== 'i') {
                handler = handler.parents('i');
            }
            let icon = handler,
                svg = $('svg', icon);
            if (svg.exists()) {
                icon = svg;
            }
            if (icon.hasClass('fa-plus-circle')) {
                const tree = icon.parents('.tree');
                MyAMS.thesaurus.tree.expandHandler(handler, tree);
            } else {
                MyAMS.thesaurus.tree.collapseHandler(handler);
            }
        },

        /**
         * Expand given tree node
         */
        expandHandler: (handler, tree) => {
            const label = handler.siblings('span.term').text();
            const spinner = $('<i></i>')
                .addClass('fas fa-fw fa-spinner fa-spin')
                .replaceAll(handler);
            MyAMS.require('ajax').then(() => {
                MyAMS.ajax.post(`${tree.data('ams-location')}/get-nodes.json`, {
                    term: label
                }).then((data) => {
                    MyAMS.thesaurus.tree.displaySubNodes(label, data.nodes, spinner);
                });
            });
        },

        /**
         * Collapse given tree node
         */
        collapseHandler: (handler) => {
            handler.parents('span.label')
                .siblings('ul.group')
                .addClass('hidden');
            handler = $('<i></i>')
                .addClass('fas fa-fw fa-plus-circle')
                .attr('data-ams-click-handler', 'MyAMS.thesaurus.tree.expandOrCollapse')
                .attr('data-ams-stop-propagation', true)
                .replaceAll(handler);
            return handler;
        },

        /**
         * Search given term and open terms tree to display it
         *
         * @param form: source form
         * @param options: object containing term *label* to search for
         */
        findTerm: (form, options) => {
            return new Promise((resolve, reject) => {
                MyAMS.require('ajax', 'alert').then(() => {
                    MyAMS.ajax.post('get-parent-nodes.json', {
                        term: options.term
                    }).then((result) => {
                        MyAMS.thesaurus.tree.displaySubNodes(result.parent, result.nodes);
                        const element = $(`span.term:withtext("${result.term}")`).parents('span.label');
                        if (element.exists()) {
                            MyAMS.ajax.check($.fn.scrollTo,
                                `${MyAMS.env.baseURL}../ext/jquery-scrollto${MyAMS.env.extext}.js`).then(() => {
                                $('#main').scrollTo(element, {offset: -15});
                                element.css('background-color', 'var(--success)')
                                    .off('mouseover')
                                    .on('mouseover', (evt) => {
                                        $(evt.target).css('background-color', '');
                                    });
                            });
                        } else if (result.term) {
                            MyAMS.require('modal').then(() => {
                                const location = $('.tree').data('ams-location');
                                MyAMS.modal.open(`${location}/++terms++/${result.term}/properties.html`);
                            });
                        }
                        resolve(element);
                    }, reject);
                });
            });
        },

        findMovedTerm: function(options) {
            return new Promise((resolve, reject) => {
                MyAMS.thesaurus.tree.findTerm(null, options).then(() => {
                    resolve();
                }, reject);
            });
        },

        /**
         * Update term label or status
         */
        updateTerm: function(form, options) {
            let handler = $(`span.term:withtext("${options.term}")`).siblings('i[data-ams-click-handler]'),
                icon;
            const svg = $('svg', handler);
            if (svg.exists()) {
                icon = svg;
            } else {
                icon = handler;
            }
            if (icon.hasClass('fa-minus-circle')) {
                handler = MyAMS.thesaurus.tree.collapseHandler(handler);
            }
            handler.click();
        },

        /**
         * Remove specified term from tree
         */
        removeTerm: function(form, options) {
            $(`span.term:withtext("${options.term}")`).parents('li').first().remove();
        },

        /**
         * Switch term extension
         *
         * @param evt: source event
         */
        switchExtension: (evt) => {
            let source = $(evt.currentTarget);
            if (evt.currentTarget.tagName.toLowerCase() !== 'i') {
                source = source.parents('i');
            }
            const
                term = source.siblings('span.label').text(),
                extension = source.data('ams-extension-name');
            MyAMS.require('ajax').then(() => {
                MyAMS.ajax.post('switch-extension.json', {
                    term: term,
                    extension: extension
                }).then((result) => {
                    source.tooltip('hide');
                    source.replaceWith($('<i></i>')
                        .addClass(result.icon)
                        .addClass('extension hint mx-2 my-1 float-right')
                        .addClass('opaque text-primary')
                        .attr('data-ams-url', result.view)
                        .attr('data-toggle', 'modal')
                        .attr('title', result.title));
                });
            });
        },

        /**
         * Extract display switcher
         *
         * This function is called via HREF reference so only returns a function
         * which will actually do the job...
         */
        switchExtract: (action) => {
            return function(link, params) {
                const
                    icon = $('i', link),
                    extract = icon.parents('tr:first').data('ams-element-name');
                let switcher;
                if (MyAMS.config.useSVGIcons) {
                    switcher = $('svg', icon);
                } else {
                    switcher = icon;
                }
                const checker = $(`i.extract-checker[data-ams-extract-name="${extract}"]`);
                if (switcher.hasClass('fa-eye-slash')) {
                    checker.css('visibility', '');
                    MyAMS.core.switchIcon(icon, 'eye-slash', 'eye');
                } else {
                    checker.css('visibility', 'hidden');
                    MyAMS.core.switchIcon(icon, 'eye', 'eye-slash');
                }
            };
        }
    },


    /**
     * Thesaurus term tree widget
     */
    widget: {

        /**
         * Initialize terms lists by adding class to lists headers containing selected terms
         */
        init: function(element) {
            $('input:checked', element).each((idx, elt) => {
                $(elt).parents('.terms-box:first')
                   .siblings('header')
                   .addClass('active');
            });
        },

        /**
         * Update header status after term (de)selection
         */
        updateSelection: (evt) => {
            let widget;
            if (evt.is && evt.is('form')) {
                widget = $('.terms-box', evt);
            } else if (evt.currentTarget.tagName.toLowerCase() === 'form') {
                widget = $('.terms-box', $(evt.currentTarget));
            } else {
                widget = $(evt.currentTarget).parents('.terms-box:first');
            }
            $(widget.each((idx, elt) => {
                const header = $(elt).siblings('header');
                header.removeClass('active');
                if ($('input:checked', elt).exists()) {
                    header.addClass('active');
                }
            }));
        }
    }
};


if (window.MyAMS) {
    MyAMS.config.modules.push('thesaurus');
    MyAMS.thesaurus = thesaurus;
    console.debug("MyAMS: thesaurus module loaded...");
}
