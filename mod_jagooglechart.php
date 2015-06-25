<?php
/**
 * ------------------------------------------------------------------------
 * JA Google Chart Module
 * ------------------------------------------------------------------------
 * Copyright (C) 2004-2011 J.O.O.M Solutions Co., Ltd. All Rights Reserved.
 * @license - GNU/GPL, http://www.gnu.org/licenses/gpl.html
 * Author: J.O.O.M Solutions Co., Ltd
 * Websites: http://www.joomlart.com - http://www.joomlancers.com
 * ------------------------------------------------------------------------
 */

defined('_JEXEC') or die('Restricted access');


//INCLUDING ASSET
require_once(dirname(__FILE__).'/asset/behavior.php');
//JHTML::_('behavior.framework', true);
include_once(dirname(__FILE__).'/asset/asset.php');

if($params->get('data_source', 'csv') == 'googlesheet'){
    $data_input = @file_get_contents($params->get('data_input_url', ''));
}else{
    $data_input = $params->get("data_input", '');
}

$rows = preg_split('/[\r\n]+/', $data_input);
$data = array();
for ($i=0;$i<count($rows);$i++) {
	$row = explode(',', str_replace(';', ',', $rows[$i]));
	$tmp = array();
	if($i==0) {
		//title
		foreach ($row as $cell) {
			$tmp[] = (string) trim($cell);
		}
	} else {
		for($j=0;$j<count($row);$j++) {
			if($j == 0) {
				$tmp[] = (string) (trim($row[$j]));//horizontal axis - item title
			} else {
				$tmp[] = (float) (trim($row[$j]));
			}
		}
	}
        if (count($tmp)>1) {
		$data[] = $tmp;
	}
}

if(count($data)) {
	$chart_description = $params->get("chart_description", '');
	//PREPARING CHART OPTIONS
	$width = $params->get("width", '100%');
	if(strpos($width, '%') === false) {
		$width = intval($width).'px';
	}
	$height = (int) $params->get("height", 600);
	$chart_type = $params->get("chart_type", 'area_chart');

	//DRAW CHART
	$funcChart = sprintf('jaDrawChart%d', $module->id);
	$container = 'ja-google-chart-wrapper-'.$module->id;
		
	$options = new stdClass();	
	$font = $params->get('font','arial');
	
	$options->backgroundColor = new stdClass();
	$options->backgroundColor->fill = $params->get('backgroundColor','#FFFFFF');
	$options->backgroundColor->stroke = $params->get('stroke','#666666');
	$options->backgroundColor->strokeWidth = $params->get('strokeWidth',0);
	
	$options->fontName = $font;
	
	// ----- Options Settings -----
	$options->width = $width;
	$options->height = $height;
	// Chart Title Settings
	$title = $params->get('chart_titleName', '');
	//$titleStyle = $params->get('chart_titleStyle','underline');
	if(!empty($title)) {
		$options->title = $title;	
		$options->titleTextStyle = new stdClass();
		$options->titleTextStyle->fontName = $params->get('chart_titleFont',$font);
		$options->titleTextStyle->fontSize = $params->get('chart_titleSize',9);
		$options->titleTextStyle->color = $params->get('chart_titleColor', '#000000');
	}

    //custom colors
    $customColors = $params->get('chart_colors', '');
    if(!empty($customColors))
    {
        $customColors = explode(',', $customColors);
        if(is_array($customColors)){
            $customColors = array_map('trim', $customColors);
            $options->colors = $customColors;
        }
    }

	// Chart Area Settings
	$options->chartArea =  new stdClass();
	$options->chartArea->left = $params->get('chartArea_left',50);
	$options->chartArea->top = $params->get('chartArea_top',50);
	$options->chartArea->width = $params->get('chartArea_width',750);
	$options->chartArea->height = $params->get('chartArea_height',500);
	
	// Legend Settings
	$options->legend = new stdClass();	
	$options->legend->position = $params->get('legend_position','right');
	$options->legend->textStyle = new stdClass();
	$options->legend->textStyle->fontName = $params->get('legend_font',$font);
	$options->legend->textStyle->fontSize = $params->get('legend_textSize',9);
	$options->legend->textStyle->color = $params->get('legend_textColor','#000000');
	
	//Tooltip setting
	$tooltip = (int) $params->get('tooltip_enabled',1);
	$tooltipTrigger = $tooltip ? 'focus' : 'none';
	$options->tooltip = new stdClass();	
	$options->tooltip->trigger = $tooltipTrigger;
	$options->tooltip->textStyle = new stdClass();
	$options->tooltip->textStyle->fontName = $params->get('tooltip_font',$font);
	$options->tooltip->textStyle->fontSize = $params->get('tooltip_textSize',9);
	$options->tooltip->textStyle->color = $params->get('tooltip_textColor','#000000');
	
	$isAxisChart = 0;
	switch ($chart_type) {
		case 'geo_chart': 
			$chart = 'GeoChart'; 
			//Options
			$options->displayMode = $params->get('geo_displayMode','regions');
			$options->region = $params->get('geo_region','world');
			$options->resolution = $params->get('geo_resolution','countries');
			$options->enableRegionInteractivity = $params->get('geo_enableRegionInteractivity', 1) ? true : false;
			$options->keepAspectRatio = $params->get('geo_keepAspectRatio', 1) ? true : false;
			$options->markerOpacity = (float) $params->get('geo_markerOpacity', 1.0);
			$options->colorAxis = new stdClass();
			$minValue = $params->get('geo_colorAxis_minValue', null);
			$maxValue = $params->get('geo_colorAxis_maxValue', null);
			if(is_null($minValue)) {
				$options->colorAxis->minValue = $minValue;
			}
			if(is_null($maxValue)) {
				$options->colorAxis->maxValue = $maxValue;
			}
			$options->colorAxis->colors = array($params->get('geo_colorAxis_fromColor', '#FFFFFF'), $params->get('geo_colorAxis_toColor', '#35A339'));
			$options->datalessRegionColor = $params->get('datalessRegionColor', '#F5F5F5');
			/*$options->magnifyingGlass = new stdClass();
			$options->magnifyingGlass->enable = true;
			$options->magnifyingGlass->zoomFactor = 5.0;*/
			break;
		case 'pie_chart': 
			$chart = 'PieChart'; 
			$options->is3D = $params->get('pie_is3D', 1) ? true : false;
			$options->reverseCategories = $params->get('pie_reverseCategories', 1) ? true : false;
			$options->pieSliceText = $params->get('pie_pieSliceText', 'percentage');
			$options->pieSliceBorderColor = $params->get('pie_pieSliceBorderColor', '#FFFFFF');
			$options->pieSliceTextStyle = new stdClass();
			$options->pieSliceTextStyle->fontName = $params->get('pieSlice_font',$font);
			$options->pieSliceTextStyle->fontSize = $params->get('pieSlice_textSize',9);
			$options->pieSliceTextStyle->color = $params->get('pieSlice_textColor','#000000');
			break;
		case 'bar_chart': 
			$chart = 'BarChart';
			$isAxisChart = 1;
			break;
		case 'column_chart': 
			$chart = 'ColumnChart'; 
			$isAxisChart = 1;
			break;
		case 'line_chart': 
			$chart = 'LineChart';
			$isAxisChart = 1;
			break;
		case 'area_chart':
		default: 
			$isAxisChart = 1;
			$chart = 'AreaChart';
			break;
	}
	
	if($isAxisChart) {
		// Horizontal Axis
		$options->hAxis = new stdClass();
		$options->reverseCategories = $params->get('axis_reverseCategories', 1) ? true : false;
		$options->lineWidth = (int) $params->get('axis_lineWidth', 2);
		$options->pointSize = (int) $params->get('axis_pointSize', 0);
		
		$hAxis_title = $params->get('hAxis_title', '');
		if(!empty($hAxis_title)) {
			$options->hAxis->title = $hAxis_title;
			$options->hAxis->titleTextStyle = new stdClass();
			$options->hAxis->titleTextStyle->fontName = $params->get('hAxis_title_font', $font);
			$options->hAxis->titleTextStyle->fontSize = $params->get('hAxis_title_textSize', 11);
			$options->hAxis->titleTextStyle->color = $params->get('hAxis_title_textColor', '#000000');
		}
		$options->hAxis->direction = (int) $params->get('hAxis_direction', 1);
		$options->hAxis->textPosition = $params->get('hAxis_textPosition', 'out');
		$options->hAxis->textStyle = new stdClass();
		$options->hAxis->textStyle->fontName = $params->get('hAxis_text_font', $font);
		$options->hAxis->textStyle->fontSize = $params->get('hAxis_text_textSize', 9);
		$options->hAxis->textStyle->color = $params->get('hAxis_text_textColor', '#000000');
		
		/*$hAxis_gridlines_enable = (int) $params->get('hAxis_gridlines_enable', 0);
		if($hAxis_gridlines_enable) {
			$options->hAxis->gridlines = new stdClass();
			$options->hAxis->gridlines->color = $params->get('hAxis_gridlines_color', '#CCCCCC');
			$options->hAxis->gridlines->count = (int) $params->get('hAxis_gridlines_count', 5);
		}
		
		$hAxis_minorGridlines_enable = (int) $params->get('hAxis_minorGridlines_enable', 0);
		if($hAxis_minorGridlines_enable) {
			$options->hAxis->minorGridlines = new stdClass();
			$options->hAxis->minorGridlines->color = $params->get('hAxis_minorGridlines_color', '#EEEEEE');
			$options->hAxis->minorGridlines->count = (int) $params->get('hAxis_minorGridlines_count', 0);
		}*/
		
		// Vertical Axis
		$options->vAxis = new stdClass();
		$vAxis_title = $params->get('vAxis_title', '');
		if(!empty($vAxis_title)) {
			$options->vAxis->title = $vAxis_title;
			$options->vAxis->titleTextStyle = new stdClass();
			$options->vAxis->titleTextStyle->fontName = $params->get('vAxis_title_font', $font);
			$options->vAxis->titleTextStyle->fontSize = $params->get('vAxis_title_textSize', 11);
			$options->vAxis->titleTextStyle->color = $params->get('vAxis_title_textColor', '#000000');
		}
		$options->vAxis->direction = (int) $params->get('vAxis_direction', 1);
		$options->vAxis->textPosition = $params->get('vAxis_textPosition', 'out');
		$options->vAxis->textStyle = new stdClass();
		$options->vAxis->textStyle->fontName = $params->get('vAxis_text_font', $font);
		$options->vAxis->textStyle->fontSize = $params->get('vAxis_text_textSize', 9);
		$options->vAxis->textStyle->color = $params->get('vAxis_text_textColor', '#000000');
		
		/*$vAxis_gridlines_enable = (int) $params->get('vAxis_gridlines_enable', 0);
		if($vAxis_gridlines_enable) {
			$options->vAxis->gridlines = new stdClass();
			$options->vAxis->gridlines->color = $params->get('vAxis_gridlines_color', '#CCCCCC');
			$options->vAxis->gridlines->count = (int) $params->get('vAxis_gridlines_count', 5);
		}
		
		$vAxis_minorGridlines_enable = (int) $params->get('vAxis_minorGridlines_enable', 0);
		if($vAxis_minorGridlines_enable) {
			$options->vAxis->minorGridlines = new stdClass();
			$options->vAxis->minorGridlines->color = $params->get('vAxis_minorGridlines_color', '#EEEEEE');
			$options->vAxis->minorGridlines->count = (int) $params->get('vAxis_minorGridlines_count', 0);
		}*/
	}
	
	$js = "
	google.setOnLoadCallback({$funcChart});
	function {$funcChart}() {
		var data = google.visualization.arrayToDataTable(".json_encode($data).");
		var options = ".json_encode($options).";
		var chart = new google.visualization.{$chart}(document.getElementById('{$container}'));
		chart.draw(data, options);
	}";
	if(strpos($width, '%') !== false) {
		JHtml::_('JABehavior.jquery');
		$js .= "
		jQuery(document).ready(function () {
			jQuery(window).resize(function(){
				{$funcChart}();
			});
		});
		";

	}
	
	$doc = JFactory::getDocument();
	$doc->addScriptDeclaration($js);
	
	require JModuleHelper::getLayoutPath($module->module, $params->get('layout', 'default'));
}
