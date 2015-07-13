/*************************************************************
	Udacity Nanodegree Project 3: Catalog App
	Author: Andrew Roy Chen
*************************************************************/

$('body').on('click', 'li', function(e) {
	e.preventDefault();
	// NOTE will treat link as async data request
	var categoryID = $(e.currentTarget).data('category-id');
	var url = "/category/" + categoryID;
	$.getJSON(url, function(data) {
		var _category_list = $(".course-list");
		var items = '';
		data.CategoryCourses.forEach(function(course) {
			var course_item = '<li class="course-list-item"><span>' + course.name +
			'</span><p>' + course.description + '</p></li><div class="divider"></div><br>';
			items += course_item;
		});
		_category_list.html('');
		_category_list.append(items);
	// 1. trigger filter of course list results
	// 2. category list gets a shadowed style and translation to appear 'lifted up'
		$('.category-container').addClass('rise');
	// 3. course list slides into view from left 'under' category list
		$('.list-container').addClass('slide-in');
	// 4. give a specific colour depending on category chosen? can add data-attribute with color
		$('.recent-posts-container').addClass('obscure');

		// set Add Course btn href attr val
		$('.btn-add-course').attr('href', url+'/add/');
	});
});

$('body').on('click', '.btn-close', function() {
		$('.list-container').removeClass('slide-in');
		setTimeout(function() {
			$('.category-container').removeClass('rise');
			$('.recent-posts-container').removeClass('obscure');
		}, 2000);

});
