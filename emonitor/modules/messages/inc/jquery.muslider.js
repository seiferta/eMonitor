/************************************************************************************************************************************************************
 * jquery.muslider-2.0.js
 * http://muslider.musings.it
 * jQuery plugin for infinite slides scrolling
 * developed for http://www.musings.it and released as a freebie
 *
 * Characteristics:
 * animations: horizontal slide, vertical slide, fade
 * images loading: lazy, only if and when it's needed
 * slides content: images, texts, audio and video html5, iframes
 * audio and video via Vimeo and YouTube including the support files you will find on http://muslider.musings.it
 * responsive with option on the ratio ("ratio") between height and width of the slider
 * "wipe-touch" support for mobiles and touch devices
 *
 * "responsive" parameter can be "yes", true or 1 (or "no", false or 0 if muslider must have fixed dimensions); default: "yes"
 * if "responsive" is "no" slider dimensions must be declared using "width" and "height" parameters (as integers NOT as %)
 * or declaring "ratio": "adjust" on the basis of each slide content (if it is an image)
 * if "responsive" is "yes", "width" and "height" parameters (slider width and height) can be declared as percentuals
 * "width": "100%"; "height": "100%" (with respect to the slider's container)
 *
 * "ratio" parameter can have these values:
 * "default" (or not set) means 9:16, thus "ratio" will be 0.5625
 * "reference": ratio between height and width of a reference image ("reference_width" and "reference_height" must be set accordingly)
 * "maximum": ratio between the max height and max width that the slider can have ("max_width" and "max_height" must be set accordingly)
 * "initial": initial ratio between height and width of the screen
 * "continuous": real time ratio between height and width of the screen (warning! this can lead to content deformation)
 * "adjust": real time ratio between height and width of the slide content (only for images)
 *
 * Configurable parameters:
 * "responsive": boolean ("yes","no"; default: "yes")
 * "ratio": ratio between slider height and width (float or string); default: 0.5625
 * "width": slider width (percentual or integer); default: "100%"
 * "height": slider height (percentual or integer); default: "100%"
 * "reference_width" (if "ratio": "reference"): reference image width (integer); default: 0
 * "reference_height" (if "ratio": "reference"): reference image height (integer); default: 0
 * "max_width" (if "ratio": "maximum"): max slider width (integer); default: 0
 * "max_height" (if "ratio": "maximum"): max slider height (integer); default: 0
 * "min_width": min slider width (integer); default: 320
 * "min_height": min slider height (integer); default: 180
 * "animation_type":  slider animation type ("horizontal", "vertical", "fade"); default "horizontal"
 * "animation_duration": animation duration (in msec); default 600
 * "animation_start": animation starting mode ("manual", "auto"); defualt "manual"
 * "animation_interval": if "animation_start": "auto" time interval between slides (in msec); default 4000
 *
 * @author Federica Sibella
 * Copyright (c) 2012-14 Federica Sibella - musings(at)musings(dot)it | http://www.musings.it
 * Licensed according to MIT license.
 * Date: 2014.02.28
 * @version 2.0
 * version log:
 * code completely re-written for multiple instance support, responsiveness and correction of some minor bugs
 *************************************************************************************************************************************************************/

(function($){
    // Global variables
    var muslider = [],
        instance = 0,
        methods = {
        // slider initialization function
        init: function(options) {
            // slider initialization function
            this.each(function() {
                    // options defaults
                    var defaults = {
                        "width": "100%",
                        "height": "100%",
                        "max_width": 0,
                        "max_height": 0,
                        "reference_width": 0,
                        "reference_height": 0,
                        "min_width": 320,
                        "min_height": 180,
                        "ratio": 0.5625, // 16:9
                        "animation_type": "horizontal",
                        "animation_duration": 600,
                        "animation_start": "manual",
                        "animation_interval": 4000,
                        "responsive": "yes"
                    },
                    $obj = $(this),
                    data = $obj.data('muslider'),
                    $options = $(),
                    $slide = $(),
                    $navslide = $(),
                    $start = $(),
                    $stop = $(),
                    $next = $(),
                    $prev = $(),
                    current = 0,
                    totslides = 0,
                    timer = 0,
                    margin = 100,
                    slider_ratio = 0.565,
                    calc_width = 0,
                    calc_height = 0;
                    $options = $.extend(defaults, options);
                    switch($options.responsive)
                    {
                        case "yes":
                        case true:
                        case 1:
                        default:
                            $options.responsive = true;
                            break;

                        case "no":
                        case false:
                        case 0:
                            $options.responsive = false;
                            break;
                    }

                    $obj.attr("data-id","muslider_" + instance);

                    // looking for all the slides
                    $slide = $obj.find(".slide");

                    // total number of slides (starts from 0!)
                    totslides = $slide.length - 1;

                    // adds to all slides an id=slide+instance+index
                    $slide.each(function(index)
                    {
                        $(this).attr("id", "slide" + instance + "_" + index);
                    });

                    // looking for slider navigation buttons
                    $navslide = $obj.next(".navslide");
                    $start = $navslide.find(".start").attr("data-id","start_"+instance);
                    $stop = $navslide.find(".stop").attr("data-id","stop_"+instance);
                    $next = $navslide.find(".next").attr("data-id","next_"+instance);
                    $prev = $navslide.find(".prev").attr("data-id","prev_"+instance);

                    // not responsive
                    if($options.responsive === false)
                    {
                        // have we got integers as width and height?
                        if(typeof($options.height) == "number" && typeof($options.width) == "number")
                        {
                            slider_ratio = $options.height / $options.width;
                            calc_width = $options.width;
                        }
                        else
                        {
                            calc_width = innum($options.width, $obj.parent().width());
                        }
                    }
                    else //responsive
                    {
                        // calculating the width (in px) relative to the container
                        calc_width = innum($options.width, $obj.parent().width());

                        // checking "ratio" to calculate the height
                        if (typeof($options.ratio) == "number")
                        {
                            slider_ratio = $options.ratio; //if it's a number, just take it as it is
                        }
                        else
                        {
                            switch($options.ratio)
                            {
                                case "default":
                                case "adjust":
                                case "":
                                default:
                                    slider_ratio = 0.5625;
                                    break;

                                case "reference":
                                    if(typeof($options.reference_height) === "number" && typeof($options.reference_width) === "number" && $options.reference_width > 0 && $options.reference_height > 0)
                                    {
                                        slider_ratio = $options.reference_height / $options.reference_width;
                                    }
                                    break;

                                case "maximum":
                                    if(typeof($options.max_height) === "number" && typeof($options.max_width) === "number" && $options.max_width > 0 && $options.max_height > 0)
                                    {
                                        slider_ratio = $options.max_height / $options.max_width;
                                    }
                                    break;

                                case "initial":
                                    slider_ratio = getCookie('muslider_ratio');
                                    if(slider_ratio == null || slider_ratio == "undefined")
                                    {
                                        calc_width = innum($options.width, $(window).width());
                                        calc_height = innum($options.height, $(window).height());
                                        slider_ratio = calc_height / calc_width;
                                        setCookie('muslider_ratio', slider_ratio);
                                    }
                                    break;

                                case "continuous":
                                    calc_width = innum($options.width, $(window).width());
                                    calc_height = innum($options.height, $(window).height());
                                    slider_ratio = calc_height / calc_width;
                                    break;
                            }
                        }
                    }

                    // calculating the slider height from width and ratio
                    calc_height = Math.round(calc_width * slider_ratio);
                    if($options.animation_type == 'fade'){
                        calc_width = "100%";
                        calc_height = "100%";
                    }
                    if($options.animation_type == 'horizonzal'){
                        calc_height = "100%";//Math.round(calc_width * slider_ratio);
                    }
                    // resizing every slide and resetting its position
                    $slide.css({
                        "box-sizing": "content-box",
                        "width": calc_width,
                        "height": calc_height,
                        "top": 0,
                        "left": 0
                    });

                    //if lazy load se the loader as image bg
                    if(typeof($slide.children("img").attr("data-src")) != "undefined" && $slide.children("img").attr("src") != $slide.children("img").attr("data-src"))
                    {
                        var loader_src = $slide.children("img").attr("src");
                        $slide.children("img").css({"background":"url("+loader_src+") no-repeat center center"});
                    }

                    // resizing every slide content
                    $slide.children("img,video,iframe").css({
                        "box-sizing": "content-box",
                        "width": calc_width,
                        "height": calc_height
                    });

                    // hiding all the slides except for the first
                    $slide.not(':first').hide();

                    // adding class "active" to the first slide
                    $slide.filter(':first').toggleClass('active');

                    // resizing the slider
                    $obj.css({
                        "box-sizing": "content-box",
                        "width": calc_width,
                        "height": calc_height
                    });

                    // saving the slider's data
                    $obj.data('muslider', {
                        slider: $obj,
                        slide: $slide,
                        totslides: totslides,
                        margin: margin,
                        navslide: $navslide,
                        start: $start,
                        stop: $stop,
                        prev: $prev,
                        next: $next,
                        current: current,
                        timer: timer,
                        options: $options,
                        instance: instance,
                        slider_ratio: slider_ratio,
                        calc_width: calc_width,
                        calc_height: calc_height
                    });

                    // checking for an image in the first slide and showing
                    load_image($obj.data('muslider'));

                    // control buttons: next
                    $next.on("click", function(e)
                    {
                        e.preventDefault();
                        $.fn.muslider('next',$(this).attr("data-id"));
                    });

                    // control buttons: prev
                    $prev.on("click", function(e)
                    {
                        e.preventDefault();
                        $.fn.muslider('prev',$(this).attr("data-id"));
                    });

                    // control buttons: stop
                    $stop.on("click", function(e)
                    {
                        e.preventDefault();
                        $.fn.muslider('stop',$(this).attr("data-id"));
                        $(this).hide();
                        $start.show();
                    });

                    // control buttons: start
                    $start.on("click", function(e)
                    {
                        e.preventDefault();
                        $.fn.muslider('start',$(this).attr("data-id"));
                        $(this).hide();
                        $stop.show();
                    });

                    // initializing wipe-touch control
                    var mm = {};
                    var swipeTreshold = 5;
                    $(document).on('touchstart', $obj, function(e)
                    {
                        if (e.originalEvent.touches == undefined)
                        {
                            var touch = e;
                        }
                        else
                        {
                            var touch = e.originalEvent.touches[0] || e.originalEvent.changedTouches[0];
                        }
                        mm.ox = touch.pageX;
                        mm.oy = touch.pageY;
                    });

                    $(document).on('touchend', $obj, function(e)
                    {
                        if (e.originalEvent.touches == undefined)
                        {
                            var touch = e;
                        }
                        else
                        {
                            var touch = e.originalEvent.touches[0] || e.originalEvent.changedTouches[0];
                        }
                        var elm = $(this).offset();
                        mm.dx = touch.pageX - mm.ox;
                        mm.dy = touch.pageY - mm.oy;

                        if (mm.dx < -swipeTreshold)
                        {
                            $next.trigger('click');
                        }
                        else if(mm.dx > swipeTreshold)
                        {
                            $prev.trigger('click');
                        }
                    });

                    // saving muslider dataS
                    data = $obj.data('muslider');
                    muslider[instance] = data;

                    // if responsive, call resize immediately
                    if($options.responsive === true)
                    {
                        $.fn.muslider('resize',instance);
                    }

                    // if animation has to start automatically: start
                    if($options.animation_start == "auto")
                    {
                        $stop.show();
                        $start.hide();
                        $.fn.muslider('start',instance);
                    }
                    else if ($options.animation_start == "manual")
                    {
                        $.fn.muslider('stop',instance);
                        $stop.hide();
                        $start.hide();
                    }

                    // increase instance and return the object
                    instance++;
                return muslider;
            });
        },
        // method for "next" command
        next: function(id) {
            id = find_instance(id);
            var data = muslider[id],
                actual = data.current;
            data.current ++;
            if(data.current > data.totslides)
            {
                data.current = 0;
            }
            // stop html5 multimedia if present
            stop_multimedia(id,actual);
            // load next image if present
            load_image(data);
            // animate slide ("n" is the direction as "next")
            animate_slide(data,actual,"n");
            // animate caption if present
            animate_caption(data);

            muslider[id] = data;
            return muslider;
        },
        // method for "prev" command
        prev: function(id) {
            id = find_instance(id);
            var data = muslider[id],
                actual = data.current;
            data.current --;
            if(data.current < 0)
            {
                data.current = data.totslides;
            }
            // stop html5 multimedia if present
            stop_multimedia(id,actual);
            // load next image if present
            load_image(data);
            // animate slide ("p" is the direction as "prev")
            animate_slide(data,actual,"p");
            // animate caption if present
            animate_caption(data);

            muslider[id] = data;
            return muslider;
        },
        // method for responsive resize
        resize: function(id) {
            id = find_instance(id);
            var data = muslider[id];
            if(data.options.responsive === true)
            {
                data = resize_slider(data);
            }
            muslider[id] = data;
            return muslider;
        },
        // method for "start" command
        start: function(id) {
            id = find_instance(id);
            var data = muslider[id];

            if(data.timer != 0)
            {
                clearInterval(data.timer);
            }

            data.timer = setInterval(function(){$.fn.muslider('next',id)},data.options.animation_interval);

            muslider[id] = data;
            return muslider;
        },
        // method for "stop" command
        stop: function(id) {
            id = find_instance(id);
            var data = muslider[id];

            clearInterval(data.timer);

            muslider[id] = data;
            return muslider;
        },
        // method for "destroy" command (if necessary)
        destroy: function() {
             id = find_instance($(this).attr("data-id"));
            var data = muslider[id];
            data.prev.off();
            data.next.off();
            $.fn.muslider('stop',id);
             $.removeData(data, this.name);
            this.removeClass(this.name);
            this.unbind();
            this.element = null;
        }
    };

    /*************************************
     * service functions
     *************************************/

    /********************************************************************************************
     * this function looks for an image in the slide, changes src content width data-src
     * for lazy load and creates the caption if necessary
     * @param {Object} data
     ********************************************************************************************/
    function load_image(data)
    {
        var $actual_slide =  $("#slide" + data.instance + "_" + data.current),
            $image = $actual_slide.find("img");

        if($image.length > 0)
        {
            // if src != data-src, change, else do nothing
            if($image.attr("src") != $image.attr("data-src"))
            {
                $image.attr("src",$image.attr("data-src"));
            }

            // checking dimensions if "ratio": "adjust" (adjusting height if it is the case)
            if(data.options.ratio == "adjust")
            {
                // actual image
                var screenImage = $image;

                // creates a new image off the screen
                var theImage = new Image();
                theImage.onload = function()
                {
                    // calculates the real dimensions
                    var imageWidth = theImage.width,
                        imageHeight = theImage.height,
                        slider_ratio = imageHeight / imageWidth,
                        $slider = data.slider,
                        $slide = data.slide,
                        calc_width = data.calc_width,
                        calc_height = Math.round(calc_width * slider_ratio);
                    // resets height relative to the calculated value
                    $actual_slide.css(
                    {
                        "height": calc_height
                    });

                    $image.css({
                        "height": calc_height
                    });

                    $slider.css(
                    {
                        "height": calc_height
                    });
                }
                theImage.src = screenImage.attr("src");
            }

            // check if there's a title and creates the caption
            if($actual_slide.find(".caption").length == 0 && $image.attr("title") != undefined && $image.attr("title") != "")
            {
                $actual_slide.append("<div class='caption'><p>" + $image.attr("title") + "</p></div>").promise().done(function()
                {
                    var bottom_position = $actual_slide.find(".caption").outerHeight(true);
                    $actual_slide.find(".caption").css({bottom: -bottom_position}).delay(800).animate({bottom:0},300);
                });
            }
        }
    }

    /***************************************
     * function for caption animation
     * @param {Object} data
     **************************************/
    function animate_caption(data)
    {
        var $actual_slide =  $("#slide" + data.instance + "_" + data.current);
        if($actual_slide.find(".caption").length > 0)
        {
            var bottom_position = $actual_slide.find(".caption").outerHeight(true);
            $actual_slide.find(".caption").css({bottom: -bottom_position}).delay(800).animate({bottom:0},300);
        }
    }

    /***************************************************************************
     * function for current slide animation
     * @param {Object} data
     * @param {Object} actual
     * @param {Object} dir
     ***************************************************************************/
    function animate_slide(data,actual,dir)
    {
        var $actual_slide =  $("#slide" + data.instance + "_" + data.current),
            $previous_slide = $("#slide" + data.instance + "_" + actual),
            $options = data.options,
            calc_width = data.calc_width,
            calc_height = data.calc_height,
            moveleft = 0,
            movetop = 0;

        // next
        if(dir == "n")
        {
            moveleft = calc_width + data.margin;
            movetop = calc_height + data.margin;
        }
        // prev
        else if(dir == "p")
        {
            moveleft = -(calc_width + data.margin);
            movetop = -(calc_height + data.margin);
        }
        // on the basis of the animation type
        switch($options.animation_type)
        {
            case "horizontal":
                $actual_slide.css({"left": moveleft}).show();
                $previous_slide.animate({"left": -(moveleft)}, $options.animation_duration,function(){$previous_slide.hide().toggleClass('active');});
                $actual_slide.animate({"left": 0}, $options.animation_duration,function(){$(this).toggleClass('active');});
                break;

            case "vertical":
                $actual_slide.css({"top": movetop}).show();
                $previous_slide.animate({"top": -(movetop)}, $options.animation_duration,function(){$previous_slide.hide().toggleClass('active');});
                $actual_slide.animate({"top": 0}, $options.animation_duration,function(){$(this).toggleClass('active');});
                break;

            case "fade":
                $previous_slide.fadeOut($options.animation_duration).toggleClass('active');
                $actual_slide.fadeIn($options.animation_duration,function(){$(this).toggleClass('active');});
                break;
        }
    }


    /***********************************************************************************
     * function that pauses html5 multimedia if present
     * @param {Object} id
     * @param {Object} actual
     **********************************************************************************/
    function stop_multimedia(id,actual)
    {
        var $previous_slide = $("#slide" + id + "_" + actual),
            $multimedia_html5;
        if($previous_slide.children().is("audio,video"))
        {
            $multimedia_html5 = $previous_slide.children("audio,video");
            if($multimedia_html5[0].paused === false)
            {
                $multimedia_html5[0].pause();
            }
        }
    }

    /**************************************************
     * function that finds muslider instance
     * @param {Object} id
     *************************************************/
    function find_instance(id)
    {
        if(typeof(id) === "string")
        {
            var position = id.indexOf("_");
            if(position != -1)
            {
                id = id.substr(position+1);
            }
        }
        return id
    }

    /*****************************************************
     * function to convert dimensions from % to px relative
     * to the parent dimension
     * @param {Object} dimension
     * @param {Object} parent_dimension
     *****************************************************/
    function innum(dim, parent_dim)
    {
        var resp_dim = dim;
        if(typeof(dim) === "string")
        {
            var position = dim.indexOf("%");
            if (position != -1)
            {
                var dim1 = parseInt(dim.slice(0,-1))/100,
                    resp_dim = parseInt(parent_dim * dim1);
            }
        }
        return resp_dim;
    }

    /**********************************************************************************************
     * function that resizes the slider relative to the parent width
     * @param {Object} data
     **********************************************************************************************/
    function resize_slider(data)
    {
        var $slider = data.slider,
            $slide = data.slide,
            $options = data.options,
            max_width = data.options.max_width,
            max_height = data.options.max_height,
            min_width = data.options.min_width,
            min_height = data.options.min_height,
            slider_ratio = data.slider_ratio,
            calc_width = data.calc_width,
            calc_height = data.calc_height,
            scrollbar_width = 40;

        calc_width = Math.min($slider.parent().width(),($(window).width()-scrollbar_width));

        if($options.ratio == "initial")
        {
            slider_ratio = getCookie('muslider_ratio');
        }
        else if($options.ratio == "continuous")
        {
            var new_width = innum($options.width, $(window).width()),
                new_height = innum($options.height, $(window).height());
            slider_ratio = new_height / new_width;
        }
        // checking dimensions if "ratio": "adjust"
        else if(data.options.ratio == "adjust")
        {
            var $actual_slide =  $("#slide" + data.instance + "_" + data.current),
                $image = $actual_slide.find("img");
            // current image
            var screenImage = $image;

            // new version of the image off screen
            var theImage = new Image();
            theImage.onload = function()
            {
                // rela dimensions
                var imageWidth = theImage.width,
                    imageHeight = theImage.height,
                    slider_ratio = imageHeight / imageWidth,
                    calc_height = Math.round(calc_width * slider_ratio);
                // resetting heights relative to the calculated value
                $actual_slide.css(
                {
                    "height": calc_height
                });

                $image.css({
                    "height": calc_height
                });

                $slider.css(
                {
                    "height": calc_height
                });
            }
            theImage.src = screenImage.attr("src");
        }

        var calc_height = Math.round(calc_width * slider_ratio);

        // checking dimensions against max dimensions (if present)
        if(max_width > 0 && calc_width > max_width)
        {
            calc_width = max_width;
            calc_height = Math.round(calc_width * slider_ratio);

            if(max_height > 0 && calc_height > max_height)
            {
                calc_height = max_height;
            }
        }

        if(max_height > 0 && calc_height > max_height)
        {
            calc_height = max_height;
            calc_width = Math.round(calc_height / slider_ratio);

            if(max_width > 0 && calc_width > max_width)
            {
                calc_width = max_width;
            }
        }

        // checking dimensions against min dimensions
        if(calc_width < min_width)
        {
            calc_width = min_width;
            calc_height = Math.round(calc_width * slider_ratio);

            if(calc_height < min_height)
            {
                calc_height = min_height;
            }
        }

        if(calc_height < min_height)
        {
            calc_height = min_height;
            calc_width = Math.round(calc_height / slider_ratio);

            if(calc_width < min_width)
            {
                calc_width = min_width;
            }
        }

        $slide.css({
            "width": calc_width,
            "height": calc_height
        });

        $slide.children("img,video,iframe").css({
            "width": calc_width,
            "height": calc_height
        });

        $slider.css({
            "width": calc_width,
            "height": calc_height
        });

        data.calc_width = calc_width;
        data.calc_height = calc_height;
        data.slide = $slide;
        data.slider = $slider;

        return data;
    }

    /****************************************************************************
     * functions that binds resize to window resize for each muslider instance
     ***************************************************************************/
    $(window).resize(function()
    {
        for(i=0;i<instance;i++)
        {
            $.fn.muslider('resize',i);
        }
    });

    /****************************************************************************************
     * function that sets a cookie (for "ratio": "initial")
     * @param {Object} name
     * @param {Object} value
     * @param {Object} days
     ****************************************************************************************/
    function setCookie(name,value,days)
    {
        if(days)
        {
            var date = new Date();
            date.setTime(date.getTime()+(days*24*60*60*1000));
            var expires = "; expires="+date.toGMTString();
        }
        else var expires = "";
        document.cookie = name+"="+value+expires+"; path=/";
    }

    /*************************************************************
     * function that gets the cookie
     * @param {Object} name
     *************************************************************/
    function getCookie(name)
    {
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        for(var i=0;i < ca.length;i++)
        {
            var c = ca[i];
            while (c.charAt(0)==' ') c = c.substring(1,c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
        }
        return null;
    }

    /**********************************************
     * function that deletes a cookie
     * @param {Object} name
     **********************************************/
    function deleteCookie(name)
    {
        setCookie(name,"",-1);
    }


    /********************************************
     * function for plugin generation
     * @param {Object} method
     ********************************************/
    $.fn.muslider = function(method)
    {
        if (methods[method])
        {
          return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        }
        else if (typeof method === 'object' || ! method)
        {
          return methods.init.apply(this, arguments);
        }
        else
        {
          $.error('Method ' +  method + ' does not exist on jQuery.muslider');
        }
      };
})(jQuery);