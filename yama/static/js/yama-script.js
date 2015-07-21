/*************************************************************
	Udacity Nanodegree Project 3: Catalog App
	Author: Andrew Roy Chen
*************************************************************/

$('.category-container').on('click', 'li', function(e) {
	e.preventDefault();
	// NOTE will treat link as async data request
	var categoryID = $(e.currentTarget).data('category-id'),
		url = '/category/' + categoryID;
	$.getJSON(url+'/json', function(data) {
		var _category_list = $(".course-list"),
			items = '';

		data.CategoryCourses.forEach(function(course) {
			var text_cutoff = course.description.length > 79 ? 80 : course.description.length, 
				course_item = '<li class="course-list-item">' + 
			'<a href="' + url + '/' + course.id + '/" class="course-list__item__link">' + 
			'<span>' + course.name + '</span><p>' + course.description.slice(0, text_cutoff) + '...' 
			+ '</p></a></li><div class="divider"></div><br>';
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

$('.main-content').on('click', '.btn-edit', function(e) {
	$('.course-item-detail').addClass('phase-out');
	$('.course-item-edit').addClass('phase-in');
});

$('body').on('click', '.btn-edit-close', function() {
	$('.course-item-detail').removeClass('phase-out');
	$('.course-item-edit').removeClass('phase-in');
});

$('.main-content').on('click', '.btn-delete', function(e) {
	$('.btn-delete-confirm').addClass('btn-slide-out');
});

$('body').on('click', '.btn-login', function(e) {
	console.log('hi');
	$('.login-modal-container').addClass('fadeIn');
});

$('body').on('click', '.btn-login-modal-close', function(e) {
	$('.login-modal-container').removeClass('fadeIn');
});
