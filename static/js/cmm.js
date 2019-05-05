$(document).ready(function () {
    $("#jump_page").click(function () {
        var max_num = $('#jump_page').data('page_num');
        var time_url = $('#jump_page').data('time_url');
        var page_num = $("#input_page").val();
        var link_url = window.location.href;
        var index = link_url.lastIndexOf("\/");
        link_url = link_url.substring(0, index + 1);
        if (page_num > max_num || !page_num) {
            if (page_num) {
                window.location.href = link_url + max_num + time_url
            }
        } else {
            window.location.href = link_url + page_num + time_url
        }
    })
});
function getTree() {
    return [
        {
            text: "参数管理",
            tags: ['available'],
            color: "#8f9baa",
            backColor: "transparent",
            href: "/parameter/1",
            levels: 1,
        },
        {
            text: "接口管理",
            tags: ['available'],
            color: "#8f9baa",
            backColor: "transparent",
            href: "/interface/1",
            levels: 1,
        },
        {
            text: "用例管理",
            tags: ['available'],
            color: "#8f9baa",
            backColor: "transparent",
            href: "/use_case/1",
            levels: 1,
            state:{
                expanded: true
            }
        },
        {
            text: "批次管理",
            tags: ['available'],
            color: "#8f9baa",
            backColor: "transparent",
            href: "/batch/1",
            levels: 1,
        },
        {
            text: "运行日志",
            tags: ['available'],
            color: "#8f9baa",
            backColor: "transparent",
            href: "/use_case_run_log/1",
            levels: 1,
        },
        {
            text: "报表",
            tags: ['available'],
            color: "#8f9baa",
            backColor: "transparent",
            href: "/use_case/report",
            levels: 1,
        },
        {
            text: "注销",
            tags: ['available'],
            color: "#8f9baa",
            backColor: "transparent",
            href: "/logout",
            levels: 1
        }]

}

function copyUseCase(selector) {
    let use_case_name = selector.value;
    console.log(use_case_name);
    $("#case_name").val(use_case_name+'-copy')
}

function pageChange(selector) {
    let page_num = selector.value;
    $('#jump_page').data('page_num',page_num)
}

function getBaseUrl() {
    var url = window.location.href;
    var url_list = url.split('/');
    return url_list[0] + '//' + url_list[1] + url_list[2];
}

function tEdited(selector) {
    console.log(111111111, selector.test)
}

function getMapfromUrl(data) {
    var base_url = getBaseUrl();
    url = base_url + data.href;
    if (data.state.selected) {
        data.state.selected = true;
        window.location.href = url;
    }

}

var treeview_data = '';
function treeview_ajax() {
    return $.ajax({
        type: 'post',
        url: '/menu_tree/info',
        data: JSON.stringify({}),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
            var menu_tree = response.res;
            treeview_data = getTree();
            treeview_data[2]['nodes'] = [];
            $.each(menu_tree, function (i, business_info) {
                treeview_data[2]['nodes'].push({
                    text: business_info.business_line.business_name,
                    tags: ['available'],
                    color: "#8f9baa",
                    backColor: "transparent",
                    levels: 2,
                    business_id:business_info.business_line.id,
                    use_case_num: 0,
                    nodes: []
                });
                if (business_info.business_line.system_line.length > 0) {
                    $.each(business_info.business_line.system_line, function (j, system_info) {
                        treeview_data[2]['nodes'][i]['nodes'].push({
                            text: system_info.system_name,
                            tags: ['available'],
                            color: "#8f9baa",
                            backColor: "transparent",
                            levels: 3,
                            select_node:'',
                            system_id:system_info.id,
                            use_case_num: 0,
                            nodes: []
                        });
                        if (system_info.function_line.length > 0) {
                            $.each(system_info.function_line, function (k, function_info) {
                                var function_text = function_info.function_name;
                                var case_num = function_info.use_case_list.length;
                                if (case_num > 0) {
                                    function_text = function_text + '(' + case_num + ')';
                                    treeview_data[2]['nodes'][i]['nodes'][j].use_case_num += case_num;
                                    treeview_data[2]['nodes'][i].use_case_num +=case_num;
                                }
                                treeview_data[2]['nodes'][i]['nodes'][j]['nodes'].push({
                                    text: function_text,
                                    tags: ['available'],
                                    color: "#8f9baa",
                                    backColor: "transparent",
                                    levels: 4,
                                    function_id: function_info.id,
                                    use_case_num: case_num,
                                    nodes: []
                                });
                                $.each(function_info.use_case_list, function(x, use_case){
                                    var use_case_text = x + 1 + '.' + use_case.use_case_name;
                                    treeview_data[2]['nodes'][i]['nodes'][j]['nodes'][k]['nodes'].push({
                                        text: use_case_text,
                                        tags: ['available'],
                                        color: "black",
                                        backColor: "#8f9baa",
                                        levels: 5,
                                        use_case_id: use_case.id,
                                        function_id: function_info.id,
                                        type: use_case.type,
                                        create_by: use_case.create_by,
                                        update_time: use_case.update_time,
                                        nodes: []
                                    })
                                });
                            });
                        }
                        if (treeview_data[2]['nodes'][i]['nodes'][j].use_case_num > 0) {
                            treeview_data[2]['nodes'][i]['nodes'][j].text += '(' + treeview_data[2]['nodes'][i]['nodes'][j].use_case_num + ')';
                        }
                    });
                }
                if (treeview_data[2]['nodes'][i].use_case_num > 0) {
                    treeview_data[2]['nodes'][i].text += '(' + treeview_data[2]['nodes'][i].use_case_num + ')';
                }
            });
        }
    });
}

function input_value(selector) {
    $(selector).next().val($(selector).val());
    $(selector).next().data($(selector).data());
    for(var i=0;i<selector.length;i++){
        var option_id = $(selector[i]).data();
        var option_value = selector[i].value;

        if($(selector).val()===option_value){
            $(selector).next().data(option_id);
            selector[i].selected = true;
            $(selector).next().val(selector[i].text);
            break;
        }
    }
}

function init_input_value(st=selector, id_name=null) {
    var input_val = $(st).val();
    var option_arr=$("option");
    var arr_option_val = []
    $("option").each(function(){  //遍历所有option
          var channlVal= $(this).val();   //获取option值
          if(channlVal!=''){
               arr_option_val.push(channlVal);  //添加到数组中
          }
     });
    if ($.inArray(input_val, arr_option_val) >= 0) {
        for(var i=0;i<option_arr.length;i++){
            var option_id = $("option").eq(i).data();
            var option_value = $("option").eq(i).val();
            if($(st).val()==option_value){
                $(st).data(option_id);
                $("option").eq(i).attr('select', true);
                break;
            }
        }
    } else {
        $(st).data(id_name, null);
    }

}

var language_cn= {
      "sProcessing": "处理中...",
      "sLengthMenu": "显示 _MENU_ 项结果",
      "sZeroRecords": "没有匹配结果",
      "sInfo": "显示第 _START_ 至 _END_ 项结果，共 _TOTAL_ 项",
      "sInfoEmpty": "显示第 0 至 0 项结果，共 0 项",
      "sInfoFiltered": "(由 _MAX_ 项结果过滤)",
      "sInfoPostFix": "",
      "sSearch": "搜索:",
      "sUrl": "",
      "sEmptyTable": "表中数据为空",
      "sLoadingRecords": "载入中...",
      "sInfoThousands": ",",
      "oPaginate": {
          "sFirst": "首页",
          "sPrevious": "上页",
          "sNext": "下页",
          "sLast": "末页"
      },
      "oAria": {
          "sSortAscending": ": 以升序排列此列",
          "sSortDescending": ": 以降序排列此列"
      }
  };

var ColorData = ['red', 'green', 'blue', 'black', 'yellow', 'orange'];
function getRandomColor() {
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 32)];
    }
    return color;
}

function sleep(n) {
    var start = new Date().getTime();
    while(true)  if(new Date().getTime()-start > n) break;
}

function syntaxHighlight(json) {
    if (typeof json != 'string') {
        json = JSON.stringify(json, undefined, 4);
    }
    json = json.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function(match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}
