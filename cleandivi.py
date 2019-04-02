#!/usr/bin/env python3
""" Parse and re-create a Divi option value """

class DiviOption:
    
    def dostr(self, count, s):
        count = int(count)
        item = s[1:1+count]
        
        s = s[1+count:]
        if s[0] != '"':
            
            
            return
        s = s[1:]
        
        return(item, s)
        
        
    def doarray(self, s):
        # We are called with count:{array-of-values}
        (count, s) = s.split(':', 1)
        itemcount = int(count)
        ret = []
        if s[0] != '{':
            
            return
        s = s[1:]
        while s[0] != '}':
            
            (key, s) = s.split(':', 1)
            
            if key == 'a':
                (count, s) = s.split(':', 1)
                (item, s) = self.doarray(count + ':' + s)
                
                
                
                s = ';' + s

            elif key == 's':
                (count, s) = s.split(':', 1)
                (item, s) = self.dostr(count, s)
            elif key == 'i':
                (count, s) = s.split(';', 1)
                s = ';' + s
                item = int(count)
            elif key == 'b':
                (count, s) = s.split(';', 1)
                s = ';' + s
                item = True if count else False
            elif key == 'd':
                (count, s) = s.split(';', 1)
                s = ';' + s
                item = float(count)
            else:
                
                
                return
            
            if s[0] == ';':
                s = s[1:]
                ret.append(item)
            elif s[0] == '}':
                ret.append(item)
            else:
                
                return
        
        

        if s[0] != '}':
            
            return    
        s = s[1:]
        return(ret, s)
        
                
        
        
    def __init__(self, s):
        work = s.strip()
        (key, work) = work.split(':', 1)
        if key != 'a':
            return    # We have problems
        (self.value, self.work) =  self.doarray(work)
        self.values = {}
        i = 0
        while i < len(self.value):
            self.values[self.value[i]] = self.value[i+1]
            i += 2
        
        

        

if __name__ == "__main__":
    value = """a:184:{s:23:"2_5_flush_rewrite_rules";s:4:"done";s:30:"divi_2_4_documentation_message";s:9:"triggered";s:15:"divi_1_3_images";s:7:"checked";s:9:"divi_logo";s:41:"https://files.d101tm.org/icons/banner.png";s:12:"divi_favicon";s:0:"";s:14:"divi_fixed_nav";s:2:"on";s:26:"divi_gallery_layout_enable";s:2:"on";s:15:"divi_grab_image";s:5:"false";s:15:"divi_blog_style";s:5:"false";s:22:"divi_shop_page_sidebar";s:16:"et_right_sidebar";s:22:"divi_mailchimp_api_key";s:0:"";s:31:"divi_regenerate_mailchimp_lists";s:5:"false";s:28:"divi_regenerate_aweber_lists";s:5:"false";s:23:"divi_show_facebook_icon";s:5:"false";s:22:"divi_show_twitter_icon";s:5:"false";s:21:"divi_show_google_icon";s:5:"false";s:18:"divi_show_rss_icon";s:5:"false";s:17:"divi_facebook_url";s:27:"https://facebook.com/d101tm";s:16:"divi_twitter_url";s:1:"#";s:15:"divi_google_url";s:1:"#";s:12:"divi_rss_url";s:0:"";s:34:"divi_woocommerce_archive_num_posts";i:9;s:17:"divi_catnum_posts";i:6;s:21:"divi_archivenum_posts";i:20;s:20:"divi_searchnum_posts";i:5;s:17:"divi_tagnum_posts";i:5;s:16:"divi_date_format";s:6:"M j, Y";s:16:"divi_use_excerpt";s:5:"false";s:26:"divi_responsive_shortcodes";s:2:"on";s:33:"divi_gf_enable_all_character_sets";s:5:"false";s:16:"divi_back_to_top";s:5:"false";s:18:"divi_smooth_scroll";s:5:"false";s:25:"divi_disable_translations";s:5:"false";s:15:"divi_custom_css";s:0:"";s:21:"divi_enable_dropdowns";s:2:"on";s:14:"divi_home_link";s:2:"on";s:15:"divi_sort_pages";s:10:"post_title";s:15:"divi_order_page";s:3:"asc";s:22:"divi_tiers_shown_pages";i:3;s:32:"divi_enable_dropdowns_categories";s:2:"on";s:21:"divi_categories_empty";s:2:"on";s:27:"divi_tiers_shown_categories";i:3;s:13:"divi_sort_cat";s:4:"name";s:14:"divi_order_cat";s:3:"asc";s:20:"divi_disable_toptier";s:5:"false";s:14:"divi_postinfo2";a:1:{i:0;s:4:"date";}s:22:"divi_show_postcomments";s:5:"false";s:15:"divi_thumbnails";s:5:"false";s:20:"divi_page_thumbnails";s:5:"false";s:23:"divi_show_pagescomments";s:5:"false";s:14:"divi_postinfo1";a:4:{i:0;s:6:"author";i:1;s:4:"date";i:2;s:10:"categories";i:3;s:8:"comments";}s:21:"divi_thumbnails_index";s:2:"on";s:19:"divi_seo_home_title";s:5:"false";s:25:"divi_seo_home_description";s:5:"false";s:22:"divi_seo_home_keywords";s:5:"false";s:23:"divi_seo_home_canonical";s:5:"false";s:23:"divi_seo_home_titletext";s:0:"";s:29:"divi_seo_home_descriptiontext";s:0:"";s:26:"divi_seo_home_keywordstext";s:0:"";s:18:"divi_seo_home_type";s:27:"BlogName | Blog description";s:22:"divi_seo_home_separate";s:3:" | ";s:21:"divi_seo_single_title";s:5:"false";s:27:"divi_seo_single_description";s:5:"false";s:24:"divi_seo_single_keywords";s:5:"false";s:25:"divi_seo_single_canonical";s:5:"false";s:27:"divi_seo_single_field_title";s:9:"seo_title";s:33:"divi_seo_single_field_description";s:15:"seo_description";s:30:"divi_seo_single_field_keywords";s:12:"seo_keywords";s:20:"divi_seo_single_type";s:21:"Post title | BlogName";s:24:"divi_seo_single_separate";s:3:" | ";s:24:"divi_seo_index_canonical";s:5:"false";s:26:"divi_seo_index_description";s:5:"false";s:19:"divi_seo_index_type";s:24:"Category name | BlogName";s:23:"divi_seo_index_separate";s:3:" | ";s:28:"divi_integrate_header_enable";s:2:"on";s:26:"divi_integrate_body_enable";s:2:"on";s:31:"divi_integrate_singletop_enable";s:2:"on";s:34:"divi_integrate_singlebottom_enable";s:2:"on";s:21:"divi_integration_head";s:0:"";s:21:"divi_integration_body";s:757:"<script>
(function(){
    // Override the addClass to prevent fixed header class from being added
    var addclass = jQuery.fn.addClass;
    jQuery.fn.addClass = function(){
        var result = addclass.apply(this, arguments);
            jQuery('#main-header').removeClass('et-fixed-header');
        return result;
    }
})();
jQuery(function($){
    $('#main-header').removeClass('et-fixed-header');
});
</script>
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-83697901-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-83697901-1');
</script>

";s:27:"divi_integration_single_top";s:0:"";s:30:"divi_integration_single_bottom";s:0:"";s:15:"divi_468_enable";s:5:"false";s:14:"divi_468_image";s:0:"";s:12:"divi_468_url";s:0:"";s:16:"divi_468_adsense";s:0:"";s:21:"et_pb_image-animation";s:3:"off";s:14:"footer_columns";s:1:"1";s:9:"footer_bg";s:7:"#ffffff";s:24:"show_footer_social_icons";b:1;s:24:"footer_widget_text_color";s:7:"#000000";s:26:"footer_widget_header_color";s:7:"#000000";s:24:"show_header_social_icons";b:1;s:12:"header_email";s:0:"";s:15:"hide_fixed_logo";b:0;s:12:"phone_number";s:0:"";s:18:"divi_color_palette";s:63:"#000000|#ffffff|#004165|#772432|#a9b2b1|#cd202c|#f2df74|#000000";s:14:"divi_menupages";a:1:{i:0;i:44;}s:12:"heading_font";s:5:"Arial";s:9:"body_font";s:5:"Arial";s:22:"fixed_secondary_nav_bg";s:7:"#000000";s:22:"fixed_menu_link_active";s:7:"#f2df74";s:21:"minimized_menu_height";i:60;s:11:"logo_height";i:100;s:15:"fixed_menu_link";s:7:"#ffffff";s:10:"font_color";s:7:"#000000";s:12:"header_color";s:7:"#000000";s:23:"secondary_nav_fullwidth";b:0;s:16:"secondary_nav_bg";s:7:"#000000";s:28:"secondary_nav_text_color_new";s:7:"#ffffff";s:32:"secondary_nav_dropdown_animation";s:4:"fade";s:13:"nav_fullwidth";b:1;s:17:"hide_primary_logo";b:0;s:31:"primary_nav_dropdown_link_color";s:7:"#ffffff";s:9:"menu_link";s:7:"#ffffff";s:14:"primary_nav_bg";s:7:"#000000";s:13:"color_schemes";s:4:"none";s:28:"footer_menu_background_color";s:21:"rgba(221,153,51,0.05)";s:22:"footer_menu_text_color";s:7:"#000000";s:29:"footer_menu_active_link_color";s:7:"#f2df74";s:27:"bottom_bar_background_color";s:7:"#772432";s:12:"accent_color";s:7:"#004165";s:23:"primary_nav_dropdown_bg";s:7:"#111111";s:31:"primary_nav_dropdown_line_color";s:7:"#004165";s:30:"primary_nav_dropdown_animation";s:4:"fade";s:21:"bottom_bar_text_color";s:7:"#ffffff";s:10:"link_color";s:7:"#0000ee";s:20:"all_buttons_bg_color";s:20:"rgba(119,36,50,0.57)";s:26:"all_buttons_bg_color_hover";s:20:"rgba(119,36,50,0.57)";s:12:"vertical_nav";b:0;s:24:"vertical_nav_orientation";s:5:"right";s:8:"hide_nav";b:0;s:21:"primary_nav_font_size";i:14;s:24:"primary_nav_font_spacing";i:0;s:12:"header_style";s:4:"left";s:16:"menu_link_active";s:7:"#f2df74";s:16:"show_search_icon";b:0;s:12:"boxed_layout";b:0;s:16:"body_font_height";d:1.5;s:25:"divi_scroll_to_anchor_fix";s:5:"false";s:25:"3_0_flush_rewrite_rules_2";s:4:"done";s:32:"et_fb_pref_settings_bar_location";s:6:"bottom";s:30:"et_fb_pref_modal_snap_location";s:4:"left";s:21:"et_fb_pref_modal_snap";s:5:"false";s:27:"et_fb_pref_modal_fullscreen";s:5:"false";s:32:"et_fb_pref_modal_dimension_width";i:1811;s:33:"et_fb_pref_modal_dimension_height";i:683;s:27:"et_fb_pref_modal_position_x";i:30;s:27:"et_fb_pref_modal_position_y";i:50;s:40:"divi_email_provider_credentials_migrated";b:1;s:21:"et_pb_static_css_file";s:2:"on";s:19:"et_pb_css_in_footer";s:3:"off";s:39:"static_css_custom_css_safety_check_done";b:1;s:30:"et_pb_static_css_cache_version";s:6:"3.0.57";s:19:"product_tour_status";a:5:{i:14;s:3:"off";i:17;s:3:"off";i:18;s:3:"off";i:9;s:3:"off";i:2;s:3:"off";}s:28:"et_fb_pref_builder_animation";s:4:"true";s:41:"et_fb_pref_builder_display_modal_settings";s:5:"false";s:21:"et_fb_pref_event_mode";s:5:"hover";s:32:"et_fb_pref_hide_disabled_modules";s:5:"false";s:28:"et_fb_pref_history_intervals";i:1;s:27:"et_fb_pref_modal_preference";s:7:"default";s:24:"et_fb_pref_toolbar_click";s:5:"false";s:26:"et_fb_pref_toolbar_desktop";s:4:"true";s:23:"et_fb_pref_toolbar_grid";s:5:"false";s:24:"et_fb_pref_toolbar_hover";s:5:"false";s:24:"et_fb_pref_toolbar_phone";s:4:"true";s:25:"et_fb_pref_toolbar_tablet";s:4:"true";s:28:"et_fb_pref_toolbar_wireframe";s:4:"true";s:23:"et_fb_pref_toolbar_zoom";s:4:"true";s:21:"et_pb_layouts_updated";b:1;s:30:"library_removed_legacy_layouts";b:1;s:24:"footer_widget_link_color";s:7:"#ffffff";s:12:"divi_sidebar";s:16:"et_right_sidebar";s:27:"divi_minify_combine_scripts";s:2:"on";s:26:"divi_minify_combine_styles";s:2:"on";s:25:"et_pb_product_tour_global";s:2:"on";s:31:"divi_previous_installed_version";s:4:"3.21";s:29:"divi_latest_installed_version";s:6:"3.21.1";s:30:"3_0_flush_rewrite_rules_3.19.3";s:4:"done";s:30:"et_flush_rewrite_rules_library";s:6:"3.21.1";s:24:"divi_show_instagram_icon";s:5:"false";s:18:"divi_instagram_url";s:1:"#";s:27:"et_pb_post_type_integration";a:4:{s:4:"post";s:2:"on";s:4:"page";s:2:"on";s:7:"project";s:2:"on";s:12:"tribe_events";s:2:"on";}s:24:"et_enable_classic_editor";s:3:"off";}"""
    v = DiviOption(value.replace('\n', '\r\n'))
    if v.work:
        print('Remaining: "%s"' % v.work)
    for k in v.values:
        print(k, v.values[k])